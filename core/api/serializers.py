from rest_framework import serializers

from core.models import Course, PromptTemplate, Student


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
