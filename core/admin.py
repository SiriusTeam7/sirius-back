from django.contrib import admin

from core.forms import ChallengeTextForm, StudentForm
from core.models import (
    Challenge,
    ChallengeRating,
    ChallengeStat,
    Company,
    Course,
    Material,
    PromptTemplate,
    SpacedRepetition,
    Student,
)


class PromptTemplateAdmin(admin.ModelAdmin):
    model = PromptTemplate
    list_display = ("type", "created_at", "updated_at")


class ChallengeAdmin(admin.ModelAdmin):
    form = ChallengeTextForm
    list_display = ("name", "text", "course", "level", "updated_at")


class ChallengeStatAdmin(admin.ModelAdmin):
    model = ChallengeStat
    list_display = ("student", "challenge", "score", "skipped", "timeout")


class ChallengeRatingAdmin(admin.ModelAdmin):
    model = ChallengeRating
    list_display = ("student", "challenge", "rating")


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ("title", "created_at", "updated_at")


class MaterialAdmin(admin.ModelAdmin):
    model = Material
    list_display = ("name", "link", "course")


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ("name", "created_at", "updated_at")


class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = ("name", "created_at", "updated_at")


class SpacedRepetitionAdmin(admin.ModelAdmin):
    model = SpacedRepetition
    list_display = (
        "student",
        "course",
        "moment1",
        "moment2",
        "moment3",
        "is_completed1",
        "is_completed2",
        "is_completed3",
    )


admin_models = [
    (PromptTemplate, PromptTemplateAdmin),
    (Challenge, ChallengeAdmin),
    (ChallengeRating, ChallengeRatingAdmin),
    (ChallengeStat, ChallengeStatAdmin),
    (Company, CompanyAdmin),
    (Course, CourseAdmin),
    (Material, MaterialAdmin),
    (SpacedRepetition, SpacedRepetitionAdmin),
    (Student, StudentAdmin),
]

for model, admin_class in admin_models:
    admin.site.register(model, admin_class)
