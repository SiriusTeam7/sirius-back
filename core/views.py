from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import PromptTemplateSerializer, StudentCourseSerializer
from core.models import PromptTemplate
from core.services.challenge import ChallengeService


class PromptTemplateView(APIView):
    def get(self, request):
        prompt_templates = PromptTemplate.objects.all()
        serializer = PromptTemplateSerializer(prompt_templates, many=True)
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
