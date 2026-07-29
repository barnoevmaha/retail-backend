from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    birthday = Column(Date, nullable=True)
    total_purchases = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    loyalty_level = Column(String(50), default="bronze")
    bonus_points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    favorites = relationship("Favorite", back_populates="customer")
    cart = relationship("Cart", uselist=False, back_populates="customer")
