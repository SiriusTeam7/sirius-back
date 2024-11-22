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

    def __str__(self):
        return f"{self.type} - {self.id}"


class Course(models.Model):
    title = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=7, default="#000000")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.id}"


class Material(models.Model):
    name = models.CharField(max_length=240)
    link = models.TextField()
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="materials", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.course.title}"


class Challenge(models.Model):
    name = models.CharField(max_length=240, null=True)
    text = models.TextField()
    level = models.PositiveSmallIntegerField(
        choices=settings.CHALLENGE_LEVEL_CHOICES, default=1
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="challenges", null=True
    )
    estimated_minutes = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Student(models.Model):
    name = models.CharField(max_length=100)
    courses = models.ManyToManyField(Course, related_name="students")
    challenges = models.ManyToManyField(Challenge, related_name="students")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


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

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"


class ChallengeStat(models.Model):
    challenge = models.ForeignKey(
        Challenge, on_delete=models.CASCADE, related_name="stats"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="challenge_stats"
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    skipped = models.BooleanField(default=False)
    timeout = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.challenge.name}"


class ChallengeRating(models.Model):
    challenge = models.ForeignKey(
        Challenge, on_delete=models.CASCADE, related_name="ratings"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="challenge_ratings"
    )
    rating = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.challenge.name}"


class SpacedRepetition(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="spaced_repetitions"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="spaced_repetitions"
    )
    moment1 = models.DateTimeField()
    is_completed1 = models.BooleanField(default=False)
    moment2 = models.DateTimeField()
    is_completed2 = models.BooleanField(default=False)
    moment3 = models.DateTimeField()
    is_completed3 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
