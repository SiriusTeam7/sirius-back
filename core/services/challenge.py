from core.services.llm_service import LLMService
from core.models import Challenge, Course, Student, StudentProgress, PromptTemplate


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

    def build_feedback_prompt(self, *args, **kwargs):
        prompt = "Build feedback prompt here."
        return prompt

    def get_challenge(self, student_id, course_id):
        try:
            challenges_made = Student.objects.get(id=student_id).challenges.all()
            new_challenge = (
                Course.objects.get(id=course_id)
                .challenges.exclude(id__in=challenges_made)
                .order_by("level")
                .first()
            )
            if new_challenge:
                return new_challenge.text

            generated_challenge = self.generate_challenge(student_id, course_id)

            if generated_challenge:
                new_challenge = Challenge.objects.create(text=generated_challenge)
                Course.objects.get(id=course_id).challenges.add(new_challenge)

            return new_challenge
        except Exception as e:
            print(e)
            return None

    def generate_challenge(self, student_id, course_id):
        prompt = self.build_challenge_prompt(student_id, course_id)
        return self.llm_service.generate_text(prompt)

    def generate_feedback(self, *args, **kwargs):
        prompt = self.build_feedback_prompt(*args, **kwargs)
        return self.llm_service.generate_text(prompt)
