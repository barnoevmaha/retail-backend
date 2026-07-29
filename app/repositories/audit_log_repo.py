from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, entity: str | None = None, action: str | None = None, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        query = self.db.query(AuditLog)
        if entity:
            query = query.filter(AuditLog.entity == entity)
        if action:
            query = query.filter(AuditLog.action == action)
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> AuditLog:
        log = AuditLog(**kwargs)
        self.db.add(log)
        self.db.commit()
        return log
