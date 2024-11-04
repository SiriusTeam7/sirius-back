from django.conf import settings

from core.models import Challenge, Course, PromptTemplate, Student, StudentProgress
from core.services.llm_service import LLMService
from core.services.utils import delete_temp_file


class ChallengeService:
    def __init__(self):
        self.llm_service = LLMService()

    def build_challenge_prompt(self, student_id, course_id):
        student_progress, _ = StudentProgress.objects.get_or_create(
            student=student_id, course=course_id
        )
        prompt_challenge_template = PromptTemplate.objects.get(type="CH")
        prompt = prompt_challenge_template.text
        prompt += (
            f"\nTranscripción del curso:  {Course.objects.get(id=course_id).transcript}"
        )
        prompt += f"\nProgreso del estudiante: {student_progress.course_progress}"
        prompt += f"\nNivel del reto: {student_progress.last_challenge_level}"
        return prompt

    def generate_challenge(self, student_id, course_id):
        prompt = self.build_challenge_prompt(student_id, course_id)
        return self.llm_service.generate_text(prompt)

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

            return new_challenge
        except Exception as e:
            print(e)
            return None

    def build_feedback_prompt(self, challenge_text, student_answer):
        prompt_challenge_template = PromptTemplate.objects.get(type="FE")
        prompt = prompt_challenge_template.text
        prompt += f"\nReto enviado al estudiante: {challenge_text}"
        prompt += f"\nRespuesta del estudiante: {student_answer}"
        return prompt

    def generate_feedback(self, challente_text, student_answer):
        prompt = self.build_feedback_prompt(challente_text, student_answer)
        return self.llm_service.generate_text(prompt)

    def get_feedback(self, student_id, challenge_id, answer_type, student_answer):
        try:
            if answer_type == settings.ANSWER_TYPE_AUDIO:
                student_answer = self.llm_service.get_text_from_audio(student_answer)
            challenge = Challenge.objects.get(id=challenge_id)
            feedback = self.generate_feedback(challenge.text, student_answer)
            Student.objects.get(id=student_id).challenges.add(challenge)
            delete_temp_file(student_answer)
            return feedback
        except Exception as e:
            print(e)
            return None
