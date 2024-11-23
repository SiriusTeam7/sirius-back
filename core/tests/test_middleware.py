from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from core.middleware import StudentMiddleware
from core.models import Student


class TestStudentMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = StudentMiddleware(get_response=lambda request: request)
        self.user = User.objects.create_user(username="testuser", password="test_pass")
        self.student = Student.objects.create(user=self.user)

    def test_authenticated_user_with_student(self):
        request = self.factory.get("/some-url/")
        request.user = self.user
        self.middleware(request)
        self.assertIsNotNone(request.student)
        self.assertEqual(request.student.id, self.student.id)

    def test_authenticated_user_without_student(self):
        user_without_student = User.objects.create_user(
            username="no_student", password="test_pass"
        )
        request = self.factory.get("/some-url/")
        request.user = user_without_student
        self.middleware(request)
        self.assertIsNone(request.student)

    def test_unauthenticated_user(self):
        request = self.factory.get("/some-url/")
        request.user = AnonymousUser()
        self.middleware(request)
        self.assertIsNone(request.student)
