from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.services.audit_service import AuditService
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"])


@router.get("")
def list_audit_logs(
    entity: str | None = None,
    action: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    service = AuditService(db)
    logs = service.list_logs(entity, action, skip, limit)
    return [AuditLogResponse.model_validate(log) for log in logs]
