from rest_framework import serializers

from core.models import PromptTemplate


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = "__all__"
