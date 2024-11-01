from django.conf import settings
import openai


class LLMService:
    def __init__(self, provider=settings.LLM_PROVIDER):
        self.provider = self._get_provider(provider)
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS

    def _get_provider(self, provider):
        if provider == settings.OPENAI_PROVIDER:
            return OpenAIProvider()
        raise ValueError("LLM API Provider not supported.")

    def generate_text(self, prompt):
        return self.provider.generate_text(prompt, self.model, self.max_tokens)


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
            print(f"Error requesting OpenAI: {e} ")
            return None
