from sqlalchemy import Column, Integer, String, Numeric

from app.core.database import Base


class LoyaltyLevel(Base):
    __tablename__ = "loyalty_levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    min_spent = Column(Numeric(12, 2), default=0)
    discount_percent = Column(Integer, default=0)
