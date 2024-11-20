import logging
import os
import tempfile
import uuid

from django.conf import settings
from rest_framework import serializers

from core.models import Challenge, Course, PromptTemplate, Student

logger = logging.getLogger(settings.LOGGER_NAME)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = "__all__"


class ChallengeSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title")
    course_color = serializers.CharField(source="course.color")

    class Meta:
        model = Challenge
        fields = ["id", "course_id", "course_title", "course_color", "text"]


class StudentCourseSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ["student_id", "course_id"]

    def validate(self, data):
        try:
            data["student"] = Student.objects.get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")

        try:
            data["course"] = Course.objects.get(id=data["course_id"])
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist.")

        return data

    def save(self):
        student = self.validated_data["student"]
        course = self.validated_data["course"]
        student.courses.add(course)
        return student


class StudentChallengeSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    challenge_id = serializers.IntegerField()
    answer_type = serializers.ChoiceField(choices=["text", "audio"])
    answer_text = serializers.CharField(required=False, default=None)
    answer_audio = serializers.FileField(required=False, default=None)

    def validate(self, data):
        try:
            data["student"] = Student.objects.get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")

        try:
            data["challenge"] = Challenge.objects.get(id=data["challenge_id"])
        except Challenge.DoesNotExist:
            raise serializers.ValidationError("Challenge does not exist.")

        error_message = "Error saving audio file."
        try:
            audio_file = data["answer_audio"]

            if data["answer_type"] == settings.ANSWER_TYPE_TEXT:
                if not data["answer_text"]:
                    error_message = "Text answer is required."
                    raise serializers.ValidationError(error_message)
                elif audio_file:
                    audio_file = None

            elif data["answer_type"] == settings.ANSWER_TYPE_AUDIO:

                if not audio_file:
                    error_message = "No audio file provided."
                    raise serializers.ValidationError(error_message)

                if audio_file and not audio_file.content_type.startswith("audio"):
                    error_message = "File is not an audio."
                    raise serializers.ValidationError(error_message)

                temp_dir = tempfile.gettempdir()
                temp_file_name = f"{str(uuid.uuid4())}{audio_file.name}"
                temp_file_path = os.path.join(temp_dir, temp_file_name)
                with open(temp_file_path, "wb") as temp_file:
                    for chunk in audio_file.chunks():
                        temp_file.write(chunk)
                data["answer_audio"] = temp_file_path
        except Exception as e:
            logger.warning(e)
            raise serializers.ValidationError(error_message)

        return data

    def save(self):
        student = self.validated_data["student"]
        challenge = self.validated_data["challenge"]
        student.challenges.add(challenge)
        return student
