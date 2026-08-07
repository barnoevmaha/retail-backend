from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.translation import SyncRequest, TranslationsResponse, SyncResponse
from app.services.translation_middleware import TranslationMiddleware

router = APIRouter(prefix="/api/translations", tags=["translations"])


@router.get("", response_model=TranslationsResponse)
def list_translations(db: Session = Depends(get_db)):
    return {"translations": TranslationMiddleware.get_all(db)}


@router.post("/sync", response_model=SyncResponse)
def sync_translations(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return {"translations": TranslationMiddleware.sync(db, payload.texts)}
