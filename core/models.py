from django.conf import settings
from django.db import models


class PromptTemplate(models.Model):
    PROMPT_TYPE_CHOICES = (
        ("CH", "Challenge"),
        ("FE", "Feedback"),
        ("CO", "Config"),
    )
    type = models.CharField(max_length=12, choices=PROMPT_TYPE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Challenge(models.Model):
    text = models.TextField()
    level = models.PositiveSmallIntegerField(choices=settings.CHALLENGE_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Course(models.Model):
    title = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Student(models.Model):
    name = models.CharField(max_length=100)
    courses = models.ManyToManyField(Course, related_name="students")
    challenges = models.ManyToManyField(Challenge, related_name="students")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentProgress(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="progresses"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_progress = models.PositiveSmallIntegerField(default=0)
    course_completed = models.BooleanField(default=False)
    last_challenge_level = models.PositiveSmallIntegerField(
        choices=settings.CHALLENGE_LEVEL_CHOICES, default=1
    )
