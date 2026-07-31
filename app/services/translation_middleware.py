from sqlalchemy.orm import Session

from app.services.translation_service import TranslationService

_service: TranslationService | None = None


def get_translation_service() -> TranslationService:
    """Process-wide singleton so the memory cache survives across requests."""
    global _service
    if _service is None:
        _service = TranslationService()
    return _service


class TranslationMiddleware:
    """HTTP facade for the translation pipeline (cache -> database -> provider)."""

    @staticmethod
    def get_all(db: Session) -> dict[str, dict]:
        return get_translation_service().get_all(db)

    @staticmethod
    def sync(db: Session, texts: list[str]) -> dict[str, dict]:
        return get_translation_service().ensure(db, texts)
