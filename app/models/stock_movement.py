from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operation = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    document_number = Column(String(100))
    reason = Column(String(500))
    comment = Column(String(500))
    performed_by_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    variant = relationship("ProductVariant", back_populates="stock_movements")
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    user = relationship("User")
