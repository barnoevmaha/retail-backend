from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    logo = Column(String(500))
    tin = Column(String(100))
