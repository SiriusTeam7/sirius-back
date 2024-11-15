from unittest.mock import Mock, mock_open, patch

from django.conf import settings
from django.test import TestCase

from core.services.llm_service import LLMService, OpenAIProvider


class LLMServiceTests(TestCase):
    @patch("core.services.llm_service.OpenAIProvider")
    def setUp(self, mock_openai_provider):
        self.mock_provider = mock_openai_provider.return_value
        self.llm_service = LLMService(provider=settings.OPENAI_PROVIDER)

    def test_llm_service_initialization(self):
        self.assertEqual(self.llm_service.provider, self.mock_provider)
        self.assertEqual(self.llm_service.model, settings.LLM_MODEL)
        self.assertEqual(
            self.llm_service.model_speech_to_text, settings.LLM_MODEL_SPEECH_TO_TEXT
        )
        self.assertEqual(self.llm_service.max_tokens, settings.LLM_MAX_TOKENS)

    def test_generate_text(self):
        self.mock_provider.generate_text.return_value = "Generated text response"
        result = self.llm_service.generate_text("Hello, world!")
        self.mock_provider.generate_text.assert_called_once_with(
            "Hello, world!", settings.LLM_MODEL, settings.LLM_MAX_TOKENS
        )
        self.assertEqual(result, "Generated text response")

    def test_get_text_from_audio(self):
        self.mock_provider.get_text_from_audio.return_value = (
            "Transcribed text from audio"
        )
        result = self.llm_service.get_text_from_audio("path/to/audio_file.wav")
        self.mock_provider.get_text_from_audio.assert_called_once_with(
            settings.LLM_MODEL_SPEECH_TO_TEXT, "path/to/audio_file.wav"
        )
        self.assertEqual(result, "Transcribed text from audio")

    def test_invalid_provider(self):
        with self.assertRaises(ValueError):
            LLMService(provider="unsupported_provider")


class OpenAIProviderTests(TestCase):
    @patch("openai.OpenAI")
    def test_generate_text(self, mock_openai_client):
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Generated text response"))]
        )
        provider = OpenAIProvider()
        result = provider.generate_text("Hello, world!", "text-davinci-003", 50)

        mock_client_instance.chat.completions.create.assert_called_once_with(
            model="text-davinci-003",
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=50,
        )
        self.assertEqual(result, "Generated text response")

    @patch("builtins.open", new_callable=mock_open, read_data="audio data")
    @patch("openai.OpenAI")
    def test_get_text_from_audio(self, mock_openai_client, mock_open):
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.audio.transcriptions.create.return_value = Mock(
            text="Transcribed text from audio"
        )
        provider = OpenAIProvider()
        result = provider.get_text_from_audio("whisper-1", "path/to/audio_file.wav")

        mock_open.assert_called_once_with("path/to/audio_file.wav", "rb")
        mock_client_instance.audio.transcriptions.create.assert_called_once_with(
            model="whisper-1", file=mock_open.return_value
        )
        self.assertEqual(result, "Transcribed text from audio")
