import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Max, OuterRef, Subquery
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import (
    ChallengeScoreSerializer,
    ChallengeSerializer,
    LoginSerializer,
    PromptTemplateSerializer,
    RegisterChallengeRatingSerializer,
    RegisterEventChallengeSerializer,
    SpacedRepetitionSerializer,
    StudentChallengeSerializer,
    StudentCourseSerializer,
    StudentCourseSummarySerializer,
)
from core.models import (
    Challenge,
    ChallengeStat,
    PromptTemplate,
    SpacedRepetition,
    Student,
)
from core.services.challenge import ChallengeService


class LoginView(APIView):
    permission_classes = [AllowAny]

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
                            "sessionid": request.session.session_key,
                            "csrftoken": request.META.get("CSRF_COOKIE"),
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

    def get(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            raise NotFound(detail="Challenge not found.")
        serializer = ChallengeSerializer(challenge)
        return Response(serializer.data)


class ChallengeScoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            raise PermissionDenied("No student profile associated with this user.")

        max_scores = (
            ChallengeStat.objects.filter(
                challenge=OuterRef("challenge"), student=student
            )
            .values("challenge")
            .annotate(max_score=Max("score"))
            .values("max_score")
        )

        stats = ChallengeStat.objects.filter(
            student=student,
            challenge__course_id=course_id,
            score__isnull=False,
            skipped=False,
            score=Subquery(max_scores),
        ).select_related("challenge")
        if not stats.exists():
            raise NotFound("No challenge stats found for the given course.")

        serializer = ChallengeScoreSerializer(stats, many=True)
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


class RegisterEventChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterEventChallengeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ChallengeStat updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterChallengeRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterChallengeRatingSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Rating registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = StudentCourseSummarySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        student = serializer.validated_data["student"]
        data = student.challenges.values("course__id", "course__title").annotate(
            total_challenges=Count("id")
        )
        return Response(data)


class SpacedRepetitionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.student
        try:
            spaced_repetition = SpacedRepetition.objects.filter(student=student)
        except SpacedRepetition.DoesNotExist:
            raise NotFound(
                "No spaced repetition record found for this student and course."
            )
        serializer = SpacedRepetitionSerializer(spaced_repetition, many=True)
        return Response(serializer.data)


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
        moment = serializer.validated_data["moment"]

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
            student_id, challenge_id, answer_type, student_answer, moment
        )
        if challenge_response is None:
            return Response(
                {"error": "Feedback could not be generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"feedback": challenge_response}, status=status.HTTP_200_OK)
