import html
import json
import logging
import urllib.parse
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranslationProviderError(Exception):
    pass


class TranslationProvider(ABC):
    """Translates a batch of English strings into one target language."""

    @abstractmethod
    def translate(self, texts: list[str], target_lang: str) -> list[str]:
        """Return one translation per input text, in the same order."""
        raise NotImplementedError


def _post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 20):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _post_form(url: str, fields: dict, headers: dict | None = None, timeout: int = 20):
    body = urllib.parse.urlencode(fields, doseq=True).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _check_alignment(translations: list[str], texts: list[str]) -> list[str]:
    if len(translations) != len(texts):
        raise TranslationProviderError(
            f"provider returned {len(translations)} translations for {len(texts)} texts"
        )
    return [t or "" for t in translations]


class GeminiProvider(TranslationProvider):
    """Google Gemini — free tier available; recommended default."""

    name = "gemini"
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    LANG_NAMES = {"ru": "Russian", "uz": "Uzbek"}

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def translate(self, texts: list[str], target_lang: str) -> list[str]:
        prompt = (
            f"Translate the following English strings to {self.LANG_NAMES[target_lang]}. "
            f'Respond with ONLY a JSON object of the form {{"translations": ["...", "..."]}} '
            f"containing exactly {len(texts)} entries in the same order as the input. "
            f"Strings:\n" + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
        )
        data = _post_json(
            f"{self.URL.format(model=self.model)}?key={self.api_key}",
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
            },
        )
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return _check_alignment(json.loads(text)["translations"], texts)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise TranslationProviderError(f"unexpected Gemini response: {e}") from e


class OpenAIProvider(TranslationProvider):
    """OpenAI Chat Completions (JSON mode)."""

    name = "openai"
    URL = "https://api.openai.com/v1/chat/completions"
    LANG_NAMES = {"ru": "Russian", "uz": "Uzbek"}

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def translate(self, texts: list[str], target_lang: str) -> list[str]:
        prompt = (
            f"Translate these English strings to {self.LANG_NAMES[target_lang]}. "
            f'Return a JSON object {{"translations": ["...", "..."]}} with exactly '
            f"{len(texts)} entries in the same order.\n" + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
        )
        data = _post_json(
            self.URL,
            {
                "model": self.model,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "You are a precise translation engine."},
                    {"role": "user", "content": prompt},
                ],
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        try:
            content = data["choices"][0]["message"]["content"]
            return _check_alignment(json.loads(content)["translations"], texts)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise TranslationProviderError(f"unexpected OpenAI response: {e}") from e


class DeepLProvider(TranslationProvider):
    """DeepL API v2 (free or pro host)."""

    name = "deepl"
    URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: str, is_pro: bool = False):
        self.api_key = api_key
        if is_pro:
            self.URL = "https://api.deepl.com/v2/translate"

    def translate(self, texts: list[str], target_lang: str) -> list[str]:
        data = _post_form(
            self.URL,
            {"text": texts, "source_lang": "EN", "target_lang": target_lang.upper()},
            headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
        )
        try:
            return _check_alignment([t["text"] for t in data["translations"]], texts)
        except (KeyError, TypeError) as e:
            raise TranslationProviderError(f"unexpected DeepL response: {e}") from e


class GoogleTranslateProvider(TranslationProvider):
    """Google Cloud Translation API v2 (API key auth)."""

    name = "google"
    URL = "https://translation.googleapis.com/language/translate/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def translate(self, texts: list[str], target_lang: str) -> list[str]:
        data = _post_json(
            f"{self.URL}?key={self.api_key}",
            {"q": texts, "source": "en", "target": target_lang, "format": "text"},
        )
        try:
            out = [html.unescape(t["translatedText"]) for t in data["data"]["translations"]]
            return _check_alignment(out, texts)
        except (KeyError, TypeError) as e:
            raise TranslationProviderError(f"unexpected Google response: {e}") from e


def get_translation_provider() -> TranslationProvider | None:
    """Return the configured provider, or the first one with an API key set."""
    providers = {
        "gemini": lambda: GeminiProvider(settings.gemini_api_key, settings.gemini_model)
        if settings.gemini_api_key
        else None,
        "openai": lambda: OpenAIProvider(settings.openai_api_key, settings.openai_model)
        if settings.openai_api_key
        else None,
        "deepl": lambda: DeepLProvider(settings.deepl_api_key) if settings.deepl_api_key else None,
        "google": lambda: GoogleTranslateProvider(settings.google_translate_api_key)
        if settings.google_translate_api_key
        else None,
    }
    if settings.translation_provider:
        selected = providers.get(settings.translation_provider)
        if selected:
            provider = selected()
            if provider:
                return provider
            logger.warning("TRANSLATION_PROVIDER=%s set but no API key configured", settings.translation_provider)
    for name, make in providers.items():
        provider = make()
        if provider:
            logger.info("Using translation provider: %s", name)
            return provider
    return None
