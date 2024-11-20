import logging

from django.conf import settings

from core.models import Challenge, Course, PromptTemplate, Student
from core.services.llm_service import LLMService
from core.services.utils import delete_temp_file


class ChallengeService:
    def __init__(self):
        self.logger = logging.getLogger(settings.LOGGER_NAME)
        self.llm_service = LLMService()

    def build_challenge_prompt(self, student_id, course_id):
        self.logger.info(
            f"Building challenge prompt for student {student_id} and course {course_id}"
        )
        prompt_challenge_template = PromptTemplate.objects.get(type="CH")
        prompt = prompt_challenge_template.text
        prompt += f"\nTranscript:  {Course.objects.get(id=course_id).transcript}"
        return prompt

    def generate_challenge(self, student_id, course_id):
        prompt = self.build_challenge_prompt(student_id, course_id)
        return self.llm_service.generate_text(
            prompt, output_schema=settings.OPENAI_CHALLENGE_SCHEMA
        )

    def get_challenge(self, student_id, course_id):
        try:
            course = Course.objects.get(id=course_id)
            challenges_made = Student.objects.get(id=student_id).challenges.all()
            new_challenge = (
                course.challenges.exclude(id__in=challenges_made)
                .order_by("level")
                .first()
            )
            if new_challenge:
                return new_challenge.text

            generated_challenge = self.generate_challenge(student_id, course_id)

            if generated_challenge:
                new_challenge = Challenge.objects.create(
                    text=generated_challenge, course=course
                )

            return new_challenge.text
        except Exception as e:
            self.logger.warning(e)
            return None

    def build_feedback_prompt(self, challenge_text, student_answer):
        prompt_challenge_template = PromptTemplate.objects.get(type="FE")
        prompt = prompt_challenge_template.text
        prompt += f"\nChallenge: {challenge_text}"
        prompt += f"\nAnswer: {student_answer}"
        return prompt

    def generate_feedback(self, challenge_text, student_answer):
        prompt = self.build_feedback_prompt(challenge_text, student_answer)
        return self.llm_service.generate_text(
            prompt, output_schema=settings.OPENAI_FEEDBACK_SCHEMA
        )

    def get_feedback(self, student_id, challenge_id, answer_type, student_answer):
        try:
            file_path = (
                student_answer if answer_type == settings.ANSWER_TYPE_AUDIO else None
            )
            if file_path:
                student_answer = self.llm_service.get_text_from_audio(file_path)
            challenge = Challenge.objects.get(id=challenge_id)
            feedback = self.generate_feedback(challenge.text, student_answer)
            Student.objects.get(id=student_id).challenges.add(challenge)
            delete_temp_file(file_path) if file_path else None
            return feedback
        except Exception as e:
            self.logger.warning(e)
        return None
