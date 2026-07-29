from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func

from app.core.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Numeric(12, 2), nullable=False)
    min_amount = Column(Numeric(12, 2), default=0)
    usage_limit = Column(Integer, default=0)
    used_count = Column(Integer, default=0)
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
