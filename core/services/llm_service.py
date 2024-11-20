import logging

import openai
from django.conf import settings
from pydantic import BaseModel


class LLMService:
    def __init__(self, provider=settings.LLM_PROVIDER):
        self.logger = logging.getLogger(settings.LOGGER_NAME)
        self.provider = self._get_provider(provider)
        self.model = settings.LLM_MODEL
        self.model_speech_to_text = settings.LLM_MODEL_SPEECH_TO_TEXT
        self.max_tokens = settings.LLM_MAX_TOKENS

    def _get_provider(self, provider):
        if provider == settings.OPENAI_PROVIDER:
            return OpenAIProvider()
        raise ValueError("LLM API Provider not supported.")

    def generate_text(self, prompt, **kwargs):
        return self.provider.generate_text(
            prompt, self.model, self.max_tokens, **kwargs
        )

    def get_text_from_audio(self, audio_file_path):
        return self.provider.get_text_from_audio(
            self.model_speech_to_text, audio_file_path
        )


class OpenAIProvider:
    class ChallengeOutputSchema(BaseModel):
        challenge: str
        hints: list[str]
        is_code_challenge: bool
        use_cases_input: list[str]
        use_cases_output: list[str]

    class FeedbackOutputSchema(BaseModel):
        feedback: str
        score_average: float
        class_recommendations: list[str]

    class MessageOutputSchema(BaseModel):
        message: str

    def __init__(self):
        self.logger = logging.getLogger(settings.LOGGER_NAME)
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI()

    def generate_text(self, prompt, model, max_tokens, **kwargs):
        output_schema = kwargs.get("output_schema", None)

        if output_schema == settings.OPENAI_CHALLENGE_SCHEMA:
            output_schema = self.ChallengeOutputSchema
        elif output_schema == settings.OPENAI_FEEDBACK_SCHEMA:
            output_schema = self.FeedbackOutputSchema
        else:
            output_schema = self.MessageOutputSchema

        try:
            response = self.client.beta.chat.completions.parse(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                response_format=output_schema,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.warning(f"Error requesting {model} OpenAI: {e} ")
            return None

    def get_text_from_audio(self, model, audio_file_path):
        try:
            audio_file = open(audio_file_path, "rb")
            transcription = self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
            )
            return transcription.text
        except Exception as e:
            self.logger.warning(f"Error requesting {model} OpenAI: {e} ")
            return None
