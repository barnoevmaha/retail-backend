from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse, NotificationSendRequest

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    channel: str | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = NotificationService(db)
    notifications = service.list(channel, status, skip, limit)
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.post("/send")
def send_notification(
    body: NotificationSendRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    service = NotificationService(db)
    notification = service.send(body.channel, body.recipient, body.message, body.title)
    return NotificationResponse.model_validate(notification)


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    service = NotificationService(db)
    notification = service.mark_read(notification_id)
    return NotificationResponse.model_validate(notification) if notification else {"ok": False}
