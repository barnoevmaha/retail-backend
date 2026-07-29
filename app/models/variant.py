from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    barcode = Column(String(100), unique=True, nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    color_id = Column(Integer, ForeignKey("colors.id"), nullable=True)
    size_id = Column(Integer, ForeignKey("sizes.id"), nullable=True)
    size = Column(String(50))  # ponytail: kept for backward compat
    color = Column(String(50))  # ponytail: kept for backward compat
    purchase_price = Column(Numeric(12, 2), default=0)
    selling_price = Column(Numeric(12, 2), default=0)
    quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="variants")
    color_rel = relationship("Color")
    size_rel = relationship("Size")
    stock_movements = relationship("StockMovement", back_populates="variant", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="variant")
    cart_items = relationship("CartItem", back_populates="variant")
