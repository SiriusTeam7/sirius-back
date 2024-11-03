from rest_framework import serializers

from core.models import Challenge, Course, PromptTemplate, Student


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = "__all__"


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
    # TODO: enable for audio
    # answer_audio = serializers.FileField(required=False)
    answer_audio = serializers.CharField(required=False, default=None)

    def validate(self, data):
        try:
            data["student"] = Student.objects.get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")

        try:
            data["challenge"] = Challenge.objects.get(id=data["challenge_id"])
        except Challenge.DoesNotExist:
            raise serializers.ValidationError("Challenge does not exist.")

        return data

    def save(self):
        student = self.validated_data["student"]
        challenge = self.validated_data["challenge"]
        student.challenges.add(challenge)
        return student
