from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import PromptTemplateSerializer
from core.models import PromptTemplate


class PromptTemplateView(APIView):
    def get(self, request):
        prompt_templates = PromptTemplate.objects.all()
        serializer = PromptTemplateSerializer(prompt_templates, many=True)
        return Response(serializer.data)
