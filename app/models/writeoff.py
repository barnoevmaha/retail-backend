from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class WriteOff(Base):
    __tablename__ = "writeoffs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(String(50), nullable=False)
    notes = Column(Text)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    items = relationship("WriteOffItem", back_populates="writeoff", cascade="all, delete-orphan")


class WriteOffItem(Base):
    __tablename__ = "writeoff_items"

    id = Column(Integer, primary_key=True, index=True)
    writeoff_id = Column(Integer, ForeignKey("writeoffs.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    writeoff = relationship("WriteOff", back_populates="items")
    variant = relationship("ProductVariant")
