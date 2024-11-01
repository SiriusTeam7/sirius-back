from django.contrib import admin

from core.models import Challenge, Course, PromptTemplate, Student, StudentProgress


class PromptTemplateAdmin(admin.ModelAdmin):
    model = PromptTemplate
    list_display = ("type", "created_at", "updated_at")


class ChallengeAdmin(admin.ModelAdmin):
    model = Challenge
    list_display = ("text", "level", "created_at", "updated_at")


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ("title", "created_at", "updated_at")


class StudentAdmin(admin.ModelAdmin):
    model = Student
    list_display = ("name", "created_at", "updated_at")


class StudentProgressAdmin(admin.ModelAdmin):
    model = StudentProgress
    list_display = (
        "student",
        "course",
        "course_progress",
        "course_completed",
        "last_challenge_level",
    )


admin_models = [
    (PromptTemplate, PromptTemplateAdmin),
    (Challenge, ChallengeAdmin),
    (Course, CourseAdmin),
    (Student, StudentAdmin),
    (StudentProgress, StudentProgressAdmin),
]

for model, admin_class in admin_models:
    admin.site.register(model, admin_class)
