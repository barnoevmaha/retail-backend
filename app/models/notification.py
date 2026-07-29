from sqlalchemy import Column, Integer, String, DateTime, Text, func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    channel = Column(String(50), nullable=False)
    title = Column(String(255))
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    recipient = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
