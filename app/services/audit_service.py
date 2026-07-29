from sqlalchemy.orm import Session

from app.repositories.audit_log_repo import AuditLogRepository
from app.models.user import User


class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditLogRepository(db)

    @staticmethod
    def _user_data(user: User | None) -> dict:
        return {"user_id": user.id if user else None, "user_email": user.email if user else None}

    def log(self, action: str, entity: str, entity_id: int | None = None, user: User | None = None, old_values: dict | None = None, new_values: dict | None = None):
        self.repo.create(
            **self._user_data(user),
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
        )

    def list_logs(self, entity: str | None = None, action: str | None = None, skip: int = 0, limit: int = 100):
        return self.repo.list_all(entity, action, skip, limit)
