from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class SmsLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False)
    message = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False)
    provider = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
