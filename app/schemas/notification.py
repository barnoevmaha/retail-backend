from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int | None
    channel: str
    title: str | None
    message: str
    status: str
    recipient: str | None
    created_at: datetime
    sent_at: datetime | None
    read_at: datetime | None

    class Config:
        from_attributes = True


class NotificationSendRequest(BaseModel):
    channel: str
    recipient: str
    title: str | None = None
    message: str
