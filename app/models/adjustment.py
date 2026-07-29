from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(String(50), nullable=False)
    notes = Column(Text)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    items = relationship("AdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")


class AdjustmentItem(Base):
    __tablename__ = "adjustment_items"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_id = Column(Integer, ForeignKey("inventory_adjustments.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    expected_quantity = Column(Integer, default=0)
    actual_quantity = Column(Integer, default=0)
    difference = Column(Integer, default=0)

    adjustment = relationship("InventoryAdjustment", back_populates="items")
    variant = relationship("ProductVariant")
