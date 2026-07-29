from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    birthday = Column(Date, nullable=True)
    avatar = Column(String(500), nullable=True)
    gender = Column(String(20), nullable=True)
    newsletter = Column(Boolean, default=False)
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")

    password_hash = Column(String(255), nullable=True)

    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    email_verification_code = Column(String(255), nullable=True)
    phone_verification_code = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    phone_verification_expires = Column(DateTime(timezone=True), nullable=True)

    password_reset_code = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    total_purchases = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    loyalty_level = Column(String(50), default="bronze")
    bonus_points = Column(Integer, default=0)

    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    is_blocked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    favorites = relationship("Favorite", back_populates="customer")
    cart = relationship("Cart", uselist=False, back_populates="customer")
    addresses = relationship("Address", back_populates="customer")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    street = Column(String(255))
    house = Column(String(50))
    apartment = Column(String(50))
    postal_code = Column(String(20))
    receiver_name = Column(String(255))
    receiver_phone = Column(String(20))
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="addresses")
