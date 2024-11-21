import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from core.api.serializers import (
    ChallengeSerializer,
    PromptTemplateSerializer,
    StudentChallengeSerializer,
    StudentCourseSerializer,
)
from core.tests.factories import TestFactory


class SerializerTests(TestFactory):

    def test_prompt_template_serializer(self):
        serializer = PromptTemplateSerializer(instance=self.prompt_challenge)
        self.assertEqual(serializer.data["type"], self.prompt_challenge.type)
        self.assertEqual(serializer.data["text"], self.prompt_challenge.text)

    def test_challenge_serializer(self):
        serializer = ChallengeSerializer(instance=self.challenge_1)
        self.assertEqual(serializer.data["id"], self.challenge_1.id)
        self.assertEqual(serializer.data["text"], self.challenge_1.text)
        self.assertEqual(serializer.data["course_id"], self.course_1.id)
        self.assertEqual(serializer.data["course_title"], self.course_1.title)
        self.assertEqual(serializer.data["course_color"], self.course_1.color)

    def test_student_course_serializer_valid(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {"course_id": self.course_1.id}
        serializer = StudentCourseSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.course_1, self.student_1.courses.all())

    def test_student_course_serializer_invalid_student(self):
        data = {"student_id": 999, "course_id": self.course_1.id}
        serializer = StudentCourseSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_course_serializer_invalid_course(self):
        data = {"student_id": self.student_1.id, "course_id": 999}
        serializer = StudentCourseSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_valid_text(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "text",
            "answer_text": "This is an answer.",
        }
        serializer = StudentChallengeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_valid_code(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "code",
            "answer_text": "print(test)",
        }
        serializer = StudentChallengeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_valid_audio(self):
        temp_file = SimpleUploadedFile(
            "test_audio.mp3", b"Audio content", content_type="audio/mpeg"
        )

        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
            "answer_audio": temp_file,
        }
        serializer = StudentChallengeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_invalid_text_missing_answer(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "text",
        }
        serializer = StudentChallengeSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_code_missing_answer(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "code",
        }
        serializer = StudentChallengeSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_audio_missing_answer(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
        }
        serializer = StudentChallengeSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_type(self):
        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "999",
        }
        serializer = StudentChallengeSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_audio(self):
        invalid_file = tempfile.NamedTemporaryFile(suffix=".txt")
        invalid_file.write(b"Invalid content")
        invalid_file.seek(0)

        data = {
            "student_id": self.student_1.id,
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
            "answer_audio": invalid_file,
        }
        serializer = StudentChallengeSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
