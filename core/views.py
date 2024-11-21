import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import (
    ChallengeSerializer,
    LoginSerializer,
    PromptTemplateSerializer,
    StudentChallengeSerializer,
    StudentCourseSerializer,
)
from core.models import Challenge, PromptTemplate
from core.services.challenge import ChallengeService


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return Response(
                    {
                        "message": "Login successful",
                        "user": {
                            "student_id": user.student.id,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class PromptTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prompt_templates = PromptTemplate.objects.all()
        serializer = PromptTemplateSerializer(prompt_templates, many=True)
        return Response(serializer.data)


class ChallengeTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        challenges = Challenge.objects.all()[:20]
        serializer = ChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


class AddCourseToStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudentCourseSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Course added to student successfully."},
            status=status.HTTP_201_CREATED,
        )


class GenerateChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudentCourseSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        student_id = serializer.validated_data["student"].id
        course_id = serializer.validated_data["course_id"]
        challenge_response = ChallengeService().get_challenge(student_id, course_id)
        if challenge_response is None:
            return Response(
                {"error": "Challenge could not be generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"challenge": challenge_response}, status=status.HTTP_200_OK)


class GenerateFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudentChallengeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        student_id = serializer.validated_data["student"].id
        challenge_id = serializer.validated_data["challenge_id"]
        answer_type = serializer.validated_data["answer_type"]
        answer_text = serializer.validated_data["answer_text"]
        answer_audio_path = serializer.validated_data["answer_audio"]

        student_answer = None

        if (
            answer_type == settings.ANSWER_TYPE_TEXT
            or answer_type == settings.ANSWER_TYPE_CODE
        ):
            student_answer = answer_text
            if student_answer is None:
                type_answer = (
                    "text" if answer_type == settings.ANSWER_TYPE_TEXT else "code"
                )
                return Response(
                    {"error": f"Answer {type_answer} is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif answer_type == settings.ANSWER_TYPE_AUDIO:
            if not os.path.exists(answer_audio_path):
                return Response(
                    {"error": "Answer audio file does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            student_answer = answer_audio_path
            if student_answer is None:
                return Response(
                    {"error": "Answer audio is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        challenge_response = ChallengeService().get_feedback(
            student_id, challenge_id, answer_type, student_answer
        )
        if challenge_response is None:
            return Response(
                {"error": "Feedback could not be generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"feedback": challenge_response}, status=status.HTTP_200_OK)
