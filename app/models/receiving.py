from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Receiving(Base):
    __tablename__ = "receivings"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    invoice_number = Column(String(255))
    received_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="receivings")
    user = relationship("User")
    items = relationship("ReceivingItem", back_populates="receiving", cascade="all, delete-orphan")


class ReceivingItem(Base):
    __tablename__ = "receiving_items"

    id = Column(Integer, primary_key=True, index=True)
    receiving_id = Column(Integer, ForeignKey("receivings.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Numeric(12, 2), default=0)

    receiving = relationship("Receiving", back_populates="items")
    variant = relationship("ProductVariant")
