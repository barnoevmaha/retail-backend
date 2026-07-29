from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(255))
    total_amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50))
    status = Column(String(50), default="completed")
    store_name = Column(String(255))
    store_address = Column(Text)
    store_phone = Column(String(50))
    store_tin = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    order = relationship("Order")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    product_name = Column(String(255))
    barcode = Column(String(50))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)

    receipt = relationship("Receipt", back_populates="items")
    variant = relationship("ProductVariant")
