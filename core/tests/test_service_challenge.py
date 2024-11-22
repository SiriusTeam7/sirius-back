from unittest.mock import patch

from django.conf import settings

from core.models import Challenge
from core.services.challenge import ChallengeService
from core.tests.factories import TestFactory


class ChallengeServiceTests(TestFactory):
    def setUp(self):
        super().setUp()
        self.service = ChallengeService()

    def test_build_challenge_prompt(self):
        prompt = self.service.build_challenge_prompt(
            student_id=self.student_1.id, course_id=self.course_1.id
        )
        self.assertIn("Template for challenge:", prompt)
        self.assertIn(self.course_1.transcript, prompt)

    @patch("core.services.llm_service.LLMService.generate_text")
    def test_generate_challenge(self, mock_generate_text):
        mock_generate_text.return_value = "Generated challenge text"

        result = self.service.generate_challenge(
            student_id=self.student_1.id, course_id=self.course_1.id
        )

        mock_generate_text.assert_called_once_with(
            f"Template for challenge: \nTranscript:  {self.course_1.transcript}",
            output_schema=settings.OPENAI_CHALLENGE_SCHEMA,
        )
        self.assertEqual(result, "Generated challenge text")

    def test_get_challenge_existing(self):
        result = self.service.get_challenge(
            student_id=self.student_1.id, course_id=self.course_1.id
        )
        self.assertEqual(result, self.challenge_1.text)

    @patch("core.services.challenge.ChallengeService.generate_challenge")
    def test_get_challenge_generate_new(self, mock_generate_challenge):
        self.student_1.challenges.add(self.challenge_1)
        self.student_1.challenges.add(self.challenge_2)

        mock_generate_challenge.return_value = "Generated challenge text"

        result = self.service.get_challenge(
            student_id=self.student_1.id, course_id=self.course_1.id
        )
        mock_generate_challenge.assert_called_once_with(
            self.student_1.id, self.course_1.id
        )

        challenge_exists = Challenge.objects.filter(
            course=self.course_1, text="Generated challenge text"
        ).exists()
        self.assertTrue(challenge_exists)
        self.assertEqual(result, "Generated challenge text")

    def test_build_feedback_prompt(self):
        prompt = self.service.build_feedback_prompt("Challenge text", "Student answer")
        self.assertIn("Template for feedback:", prompt)
        self.assertIn("Challenge text", prompt)
        self.assertIn("Student answer", prompt)

    @patch("core.services.llm_service.LLMService.generate_text")
    def test_generate_feedback(self, mock_generate_text):
        mock_generate_text.return_value = "Generated feedback text"

        result = self.service.generate_feedback("Challenge text", "Student answer")

        mock_generate_text.assert_called_once_with(
            "Template for feedback: \nChallenge: Challenge text\nAnswer: Student answer",
            output_schema=settings.OPENAI_FEEDBACK_SCHEMA,
        )
        self.assertEqual(result, "Generated feedback text")

    @patch("core.services.challenge.is_spaced_repetition_check")
    @patch("core.services.challenge.delete_temp_file")
    @patch("core.services.llm_service.LLMService.get_text_from_audio")
    @patch("core.services.llm_service.LLMService.generate_text")
    def test_get_feedback_audio(
        self,
        mock_generate_text,
        mock_get_text_from_audio,
        mock_delete_temp_file,
        mock_is_spaced_repetition_check,
    ):
        mock_get_text_from_audio.return_value = "Transcribed text"
        mock_generate_text.return_value = "Generated feedback text"

        result = self.service.get_feedback(
            student_id=self.student_1.id,
            challenge_id=self.challenge_1.id,
            answer_type="audio",
            student_answer="path/to/audio",
            moment=None,
        )

        mock_get_text_from_audio.assert_called_once_with("path/to/audio")
        mock_generate_text.assert_called_once_with(
            f"Template for feedback: \nChallenge: {self.challenge_1.text}\nAnswer: Transcribed text",
            output_schema=settings.OPENAI_FEEDBACK_SCHEMA,
        )
        mock_delete_temp_file.assert_called_once_with("path/to/audio")
        mock_is_spaced_repetition_check.assert_not_called()
        self.assertEqual(result, "Generated feedback text")

    @patch("core.services.challenge.is_spaced_repetition_check")
    @patch("core.services.challenge.delete_temp_file")
    @patch("core.services.llm_service.LLMService.get_text_from_audio")
    @patch("core.services.llm_service.LLMService.generate_text")
    def test_get_feedback_text(
        self,
        mock_generate_text,
        mock_get_text_from_audio,
        mock_delete_temp_file,
        mock_is_spaced_repetition_check,
    ):
        mock_generate_text.return_value = "Generated feedback text"

        result = self.service.get_feedback(
            student_id=self.student_1.id,
            challenge_id=self.challenge_1.id,
            answer_type="text",
            student_answer="Transcribed text",
            moment=1,
        )

        mock_get_text_from_audio.assert_not_called()
        mock_generate_text.assert_called_once_with(
            f"Template for feedback: \nChallenge: {self.challenge_1.text}\nAnswer: Transcribed text",
            output_schema=settings.OPENAI_FEEDBACK_SCHEMA,
        )
        mock_delete_temp_file.assert_not_called()
        mock_is_spaced_repetition_check.assert_called_once_with(
            self.student_1.id, self.course_1.id, 1
        )
        self.assertEqual(result, "Generated feedback text")
