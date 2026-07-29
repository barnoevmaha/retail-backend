from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text)
    status = Column(String(50), nullable=False, default="draft")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order")
    customer = relationship("Customer")
    user = relationship("User")
    items = relationship("ReturnItem", back_populates="return_", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), default=0)

    return_ = relationship("Return", back_populates="items")
    variant = relationship("ProductVariant")
