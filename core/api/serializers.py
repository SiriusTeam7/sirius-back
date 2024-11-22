import logging
import os
import tempfile
import uuid

from django.conf import settings
from rest_framework import serializers

from core.models import (
    Challenge,
    ChallengeRating,
    ChallengeStat,
    Course,
    PromptTemplate,
    Student,
)

logger = logging.getLogger(settings.LOGGER_NAME)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = "__all__"


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = "__all__"


class ChallengeScoreSerializer(serializers.ModelSerializer):
    challenge_name = serializers.CharField(source="challenge.name")
    challenge_estimated_time = serializers.IntegerField(
        source="challenge.estimated_minutes"
    )

    class Meta:
        model = ChallengeStat
        fields = ["challenge_name", "score", "challenge_estimated_time"]


class RegisterEventChallengeSerializer(serializers.ModelSerializer):
    challenge_id = serializers.IntegerField(write_only=True)
    skipped = serializers.BooleanField(required=False, default=False)
    timeout = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = ChallengeStat
        fields = ["challenge_id", "skipped", "timeout"]

    def validate_challenge_id(self, value):
        try:
            Challenge.objects.get(id=value)
        except Challenge.DoesNotExist:
            raise serializers.ValidationError(
                "Challenge with the given ID does not exist."
            )
        return value

    def validate(self, data):
        skipped = data.get("skipped", False)
        timeout = data.get("timeout", False)
        if skipped == timeout:
            raise serializers.ValidationError(
                "Either skipped or timeout must be True and the other False."
            )
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        student = Student.objects.get(user=request.user)
        challenge = Challenge.objects.get(id=validated_data["challenge_id"])
        challenge_stat = ChallengeStat.objects.create(
            challenge=challenge,
            student=student,
            skipped=validated_data.get("skipped", False),
            timeout=validated_data.get("timeout", False),
        )
        return challenge_stat


class StudentCourseSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ["course_id"]

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.student:
            raise serializers.ValidationError(
                "No student associated with this session."
            )

        data["student"] = request.student

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


class StudentCourseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = []

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.student:
            raise serializers.ValidationError(
                "No student associated with this session."
            )
        data["student"] = request.student
        return data

    def save(self):
        student = self.validated_data["student"]
        return student


class StudentChallengeSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField()
    answer_type = serializers.ChoiceField(choices=["audio", "code", "text"])
    answer_text = serializers.CharField(required=False, default=None)
    answer_audio = serializers.FileField(required=False, default=None)
    moment = serializers.ChoiceField(
        choices=settings.SPACED_REPETITION_MOMENT_CHOICES, required=False, default=None
    )

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.student:
            raise serializers.ValidationError(
                "No student associated with this session."
            )

        data["student"] = request.student

        try:
            data["challenge"] = Challenge.objects.get(id=data["challenge_id"])
        except Challenge.DoesNotExist:
            raise serializers.ValidationError("Challenge does not exist.")

        error_message = "Error saving audio file."
        try:
            audio_file = data["answer_audio"]

            if (
                data["answer_type"] == settings.ANSWER_TYPE_TEXT
                or data["answer_type"] == settings.ANSWER_TYPE_CODE
            ):
                if not data["answer_text"]:
                    type_answer = (
                        "text"
                        if data["answer_type"] == settings.ANSWER_TYPE_TEXT
                        else "code"
                    )
                    error_message = f"{type_answer.capitalize()} answer is required."
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


class RegisterChallengeRatingSerializer(serializers.ModelSerializer):
    challenge_id = serializers.IntegerField(write_only=True)
    rating = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = ChallengeRating
        fields = ["challenge_id", "rating"]

    def validate_challenge_id(self, value):
        if not Challenge.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Challenge with the given ID does not exist."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        student = Student.objects.get(user=request.user)
        challenge = Challenge.objects.get(id=validated_data["challenge_id"])
        rating = ChallengeRating.objects.create(
            challenge=challenge, student=student, rating=validated_data["rating"]
        )
        return rating
