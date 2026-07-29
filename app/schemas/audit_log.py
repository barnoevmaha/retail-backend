from pydantic import BaseModel
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    user_email: str | None
    action: str
    entity: str
    entity_id: int | None
    old_values: dict | None
    new_values: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
