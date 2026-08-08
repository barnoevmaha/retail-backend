from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, func

from app.core.database import Base


class PosSession(Base):
    __tablename__ = "pos_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    status = Column(String(50), default="active")
    items = Column(Text)
    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(255))
    customer_phone = Column(String(50))
    payment_method = Column(String(50))
    total = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
