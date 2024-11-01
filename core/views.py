from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import PromptTemplateSerializer, StudentCourseSerializer
from core.models import PromptTemplate


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
