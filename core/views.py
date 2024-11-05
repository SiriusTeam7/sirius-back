import os

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import (
    ChallengeSerializer,
    PromptTemplateSerializer,
    StudentChallengeSerializer,
    StudentCourseSerializer,
)
from core.models import Challenge, PromptTemplate
from core.services.challenge import ChallengeService


class PromptTemplateView(APIView):
    def get(self, request):
        prompt_templates = PromptTemplate.objects.all()
        serializer = PromptTemplateSerializer(prompt_templates, many=True)
        return Response(serializer.data)


class ChallengeTemplateView(APIView):
    def get(self, request):
        challenges = Challenge.objects.all().order_by("?")[:20]
        serializer = ChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


class AddCourseToStudentView(APIView):
    def post(self, request):
        serializer = StudentCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Course added to student successfully."},
            status=status.HTTP_201_CREATED,
        )


class GenerateChallengeView(APIView):
    def post(self, request):
        serializer = StudentCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_id = serializer.validated_data["student_id"]
        course_id = serializer.validated_data["course_id"]
        challenge_response = ChallengeService().get_challenge(student_id, course_id)
        if challenge_response is None:
            return Response(
                {"error": "Challenge coudn't be generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"challenge": challenge_response}, status=status.HTTP_200_OK)


class GenerateFeedbackView(APIView):
    def post(self, request):
        serializer = StudentChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_id = serializer.validated_data["student_id"]
        challenge_id = serializer.validated_data["challenge_id"]
        answer_type = serializer.validated_data["answer_type"]
        answer_text = serializer.validated_data["answer_text"]
        answer_audio_path = serializer.validated_data["answer_audio"]

        student_answer = None

        if answer_type == settings.ANSWER_TYPE_TEXT:
            student_answer = answer_text
            if student_answer is None:
                return Response(
                    {"error": "Answer text is required."},
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
                {"error": "Feedback coudn't be generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"feedback": challenge_response}, status=status.HTTP_200_OK)
