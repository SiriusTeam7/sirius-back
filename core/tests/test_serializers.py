import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from core.api.serializers import (
    ChallengeScoreSerializer,
    ChallengeSerializer,
    PromptTemplateSerializer,
    RegisterEventChallengeSerializer,
    StudentChallengeSerializer,
    StudentCourseSerializer,
    StudentCourseSummarySerializer,
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
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = None
        data = {"course_id": self.course_1.id}
        serializer = StudentCourseSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_course_serializer_invalid_course(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {"course_id": 999}
        serializer = StudentCourseSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_valid_text(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "text",
            "answer_text": "This is an answer.",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_valid_code(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "code",
            "answer_text": "print(test)",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_valid_audio(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        temp_file = SimpleUploadedFile(
            "test_audio.mp3", b"Audio content", content_type="audio/mpeg"
        )

        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
            "answer_audio": temp_file,
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertIn(self.challenge_1, self.student_1.challenges.all())

    def test_student_challenge_serializer_invalid_text_missing_answer(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "text",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_code_missing_answer(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "code",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_audio_missing_answer(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_type(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "999",
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_challenge_serializer_invalid_audio(self):
        request = self.request_factory.get("/test/")
        request.user = self.user_1
        request.student = self.student_1
        invalid_file = tempfile.NamedTemporaryFile(suffix=".txt")
        invalid_file.write(b"Invalid content")
        invalid_file.seek(0)

        data = {
            "challenge_id": self.challenge_1.id,
            "answer_type": "audio",
            "answer_audio": invalid_file,
        }
        serializer = StudentChallengeSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_student_course_summary_serializer_valid(self):
        request = self.request_factory.get("/")
        request.student = self.student_1
        serializer = StudentCourseSummarySerializer(
            data={}, context={"request": request}
        )
        self.assertTrue(serializer.is_valid())
        saved_student = serializer.save()
        self.assertEqual(saved_student, self.student_1)

    def test_challenge_score_serializer(self):
        serializer = ChallengeScoreSerializer(instance=self.challenge_stat_1)
        expected_data = {
            "challenge_name": self.challenge_1.name,
            "score": "8.50",
            "challenge_estimated_time": self.challenge_1.estimated_minutes,
        }
        self.assertEqual(serializer.data, expected_data)

    def challenge_score_serializer_skipped_challenge(self):
        serializer = ChallengeScoreSerializer(instance=self.challenge_stat_3)
        expected_data = {
            "challenge_name": "Challenge 2",
            "score": "0.00",
            "challenge_estimated_time": self.challenge_2.estimated_minutes,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_register_event_challenge_skipped_true(self):
        request = self.request_factory.get("/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "skipped": True,
            "timeout": False,
        }
        serializer = RegisterEventChallengeSerializer(
            data=data, context={"request": request}
        )
        self.assertTrue(serializer.is_valid())
        challenge_stat = serializer.save()
        self.assertEqual(challenge_stat.skipped, True)
        self.assertEqual(challenge_stat.timeout, False)

    def test_valid_data_timeout_true(self):
        request = self.request_factory.get("/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "skipped": False,
            "timeout": True,
        }
        serializer = RegisterEventChallengeSerializer(
            data=data, context={"request": request}
        )
        self.assertTrue(serializer.is_valid())
        challenge_stat = serializer.save()
        self.assertEqual(challenge_stat.skipped, False)
        self.assertEqual(challenge_stat.timeout, True)

    def test_invalid_both_false(self):
        request = self.request_factory.get("/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "skipped": False,
            "timeout": False,
        }
        serializer = RegisterEventChallengeSerializer(
            data=data, context={"request": request}
        )
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Either skipped or timeout must be True and the other False.",
            str(e.exception),
        )

    def test_invalid_both_true(self):
        request = self.request_factory.get("/")
        request.user = self.user_1
        request.student = self.student_1
        data = {
            "challenge_id": self.challenge_1.id,
            "skipped": True,
            "timeout": True,
        }
        serializer = RegisterEventChallengeSerializer(
            data=data, context={"request": request}
        )
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Either skipped or timeout must be True and the other False.",
            str(e.exception),
        )
