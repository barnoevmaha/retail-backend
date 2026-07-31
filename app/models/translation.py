from sqlalchemy import Column, Integer, String, Text, DateTime, func

from app.core.database import Base


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(500), unique=True, nullable=False, index=True)
    en = Column(Text, nullable=False)
    ru = Column(Text, nullable=False, default="")
    uz = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
