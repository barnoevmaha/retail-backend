from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.sms import SmsLog
from app.services.sms_service import SmsService

router = APIRouter(prefix="/api/sms", tags=["sms"])


class SmsSendRequest(BaseModel):
    phone: str
    message: str


@router.post("/send")
def send_sms(
    body: SmsSendRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    service = SmsService(db)
    success = service.send(body.phone, body.message)
    return {"success": success}


@router.get("/logs")
def list_sms_logs(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    logs = db.query(SmsLog).order_by(SmsLog.created_at.desc()).limit(100).all()
    return [
        {"id": l.id, "phone": l.phone, "message": l.message, "status": l.status, "created_at": l.created_at.isoformat()}
        for l in logs
    ]
