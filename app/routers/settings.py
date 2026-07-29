from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.setting_repo import SettingRepository
from app.schemas.setting import SettingResponse, SettingUpsert

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def list_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return [SettingResponse.model_validate(s) for s in SettingRepository(db).all()]


@router.post("", response_model=SettingResponse)
def upsert_setting(
    body: SettingUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return SettingRepository(db).set(body.key, body.value)


@router.get("/{key}")
def get_setting(key: str, db: Session = Depends(get_db)):
    value = SettingRepository(db).get(key)
    return {"key": key, "value": value}
