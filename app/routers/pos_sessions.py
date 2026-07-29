from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.pos_session_service import PosSessionService
from app.schemas.pos_session import PosSessionCreate, PosSessionUpdate, PosSessionResponse

router = APIRouter(prefix="/api/pos-sessions", tags=["pos-sessions"])


@router.get("")
def list_suspended(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    service = PosSessionService(db)
    sessions = service.list_suspended()
    return [PosSessionResponse.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=PosSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    service = PosSessionService(db)
    return service.get(session_id)


@router.post("", response_model=PosSessionResponse)
def suspend_sale(
    body: PosSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    service = PosSessionService(db)
    return service.suspend(body, user)


@router.put("/{session_id}/resume", response_model=PosSessionResponse)
def resume_sale(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    service = PosSessionService(db)
    return service.resume(session_id, user)


@router.put("/{session_id}/cancel", response_model=PosSessionResponse)
def cancel_sale(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    service = PosSessionService(db)
    return service.cancel(session_id, user)
