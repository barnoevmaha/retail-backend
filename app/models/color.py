from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Color(Base):
    __tablename__ = "colors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    hex_value = Column(String(7))
