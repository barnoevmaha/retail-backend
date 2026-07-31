import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.translation_repo import TranslationRepository
from app.services.translation_cache import TranslationCache
from app.services.translation_provider import TranslationProvider, get_translation_providers

logger = logging.getLogger(__name__)


class TranslationService:
    """Resolves UI strings via memory cache -> database -> translation API."""

    def __init__(self, provider: Optional[TranslationProvider] = None):
        self.cache = TranslationCache()
        self.providers = [provider] if provider is not None else get_translation_providers()

    def get_all(self, db: Session) -> dict[str, dict]:
        repo = TranslationRepository(db)
        rows = repo.get_all()
        result = {r.key: {"key": r.key, "en": r.en, "ru": r.ru, "uz": r.uz} for r in rows}
        self.cache.prime(rows)
        return result

    def ensure(self, db: Session, texts: list[str]) -> dict[str, dict]:
        """Return translations for every text; translate + persist the missing ones."""
        texts = list(dict.fromkeys(t for t in (x.strip() for x in texts) if t))
        if not texts:
            return {}

        found, missing = self.cache.get_many(texts)
        if missing:
            repo = TranslationRepository(db)
            db_rows = repo.get_many(missing)
            for key, row in db_rows.items():
                entry = {"key": key, "en": row.en, "ru": row.ru, "uz": row.uz}
                found[key] = entry
                self.cache.set_many({key: entry})

            still_missing = [k for k in missing if k not in db_rows]
            if still_missing:
                entries = self._translate(still_missing)
                repo.upsert_many(list(entries.values()))
                self.cache.set_many(entries)
                found.update(entries)
        return found

    def _translate(self, texts: list[str]) -> dict[str, dict]:
        """Ask configured providers for ru + uz, falling back to the next provider and finally English."""
        entries = {key: {"key": key, "en": key, "ru": key, "uz": key} for key in texts}
        if not self.providers:
            logger.warning("No translation provider configured — %d strings stay English", len(texts))
            return entries
        for lang in ("ru", "uz"):
            for provider in self.providers:
                try:
                    translated = provider.translate(texts, lang)
                except Exception as e:
                    logger.warning("Translation provider %s failed for %s: %s", provider.name, lang, e)
                    continue
                for key, value in zip(texts, translated):
                    entries[key][lang] = value or key
                break
        return entries
