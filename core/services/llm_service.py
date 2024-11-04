import openai
from django.conf import settings


class LLMService:
    def __init__(self, provider=settings.LLM_PROVIDER):
        self.provider = self._get_provider(provider)
        self.model = settings.LLM_MODEL
        self.model_speech_to_text = settings.LLM_MODEL_SPEECH_TO_TEXT
        self.max_tokens = settings.LLM_MAX_TOKENS

    def _get_provider(self, provider):
        if provider == settings.OPENAI_PROVIDER:
            return OpenAIProvider()
        raise ValueError("LLM API Provider not supported.")

    def generate_text(self, prompt):
        return self.provider.generate_text(prompt, self.model, self.max_tokens)

    def get_text_from_audio(self, audio_file_path):
        return self.provider.get_text_from_audio(
            self.model_speech_to_text, audio_file_path
        )


class OpenAIProvider:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI()

    def generate_text(self, prompt, model, max_tokens):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error requesting {model} OpenAI: {e} ")
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
            print(f"Error requesting {model} OpenAI: {e} ")
            return None
