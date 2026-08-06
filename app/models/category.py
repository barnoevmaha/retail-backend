from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(500))
    image = Column(String(500))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    size_system = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")
