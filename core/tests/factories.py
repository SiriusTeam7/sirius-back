from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from core.models import Challenge, Course, PromptTemplate, Student


class TestFactory(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        User = get_user_model()
        self.user_1 = User.objects.create_user(
            username="user_t1", email="t1@test.com", password="pwd1"
        )
        self.user_2 = User.objects.create_user(
            username="user_t2", email="t2@test.com", password="pwd2"
        )

        self.prompt_challenge = PromptTemplate.objects.create(
            type="CH", text="Template for challenge: "
        )
        self.prompt_feedback = PromptTemplate.objects.create(
            type="FE", text="Template for feedback: "
        )

        self.course_1 = Course.objects.create(
            id=1, title="Test Course 1", transcript="transcript for testing."
        )
        self.course_2 = Course.objects.create(
            id=2, title="Test Course 2", transcript="transcript for testing."
        )

        self.challenge_1 = Challenge.objects.create(
            id=1, text="Challenge 1", course=self.course_1, level=1
        )
        self.challenge_2 = Challenge.objects.create(
            id=2, text="Challenge 2", course=self.course_1, level=2
        )
        self.challenge_3 = Challenge.objects.create(
            id=3, text="Challenge 3", course=self.course_2, level=2
        )

        self.student_1 = Student.objects.create(
            id=1, name="Test Student 1", user=self.user_1
        )
        self.student_2 = Student.objects.create(
            id=2, name="Test Student 2", user=self.user_2
        )
