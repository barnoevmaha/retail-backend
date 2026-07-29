from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Size(Base):
    __tablename__ = "sizes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    sort_order = Column(Integer, default=0)
