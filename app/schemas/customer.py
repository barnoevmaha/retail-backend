from pydantic import BaseModel, field_validator
from datetime import date, datetime
import re


# --- Existing schemas (unchanged) ---

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    birthday: date | None = None


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    birthday: date | None = None


class CustomerResponse(BaseModel):
    id: int
    user_id: int | None
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    birthday: date | None
    gender: str | None
    newsletter: bool
    language: str
    timezone: str
    email_verified: bool
    phone_verified: bool
    total_purchases: int
    total_spent: float
    loyalty_level: str
    bonus_points: int
    last_login: datetime | None
    is_blocked: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Registration ---

class RegisterEmailRequest(BaseModel):
    first_name: str
    last_name: str
    email: str


class RegisterEmailVerifyRequest(BaseModel):
    email: str
    code: str
    password: str
    confirm_password: str


class RegisterPhoneRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str


class RegisterPhoneVerifyRequest(BaseModel):
    phone: str
    code: str
    password: str
    confirm_password: str


# --- Login ---

class CustomerLoginRequest(BaseModel):
    login: str
    password: str


class CustomerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse


# --- Verification ---

class VerifyCodeRequest(BaseModel):
    identifier: str
    code: str


class SendCodeRequest(BaseModel):
    identifier: str


# --- Password ---

class ForgotPasswordRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    identifier: str
    code: str
    new_password: str
    confirm_password: str


# --- Link email/phone ---

class LinkEmailRequest(BaseModel):
    email: str


class LinkEmailVerifyRequest(BaseModel):
    email: str
    code: str


class LinkPhoneRequest(BaseModel):
    phone: str


class LinkPhoneVerifyRequest(BaseModel):
    phone: str
    code: str


# --- Profile ---

class CustomerProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    avatar: str | None = None
    gender: str | None = None
    newsletter: bool | None = None
    language: str | None = None
    timezone: str | None = None


# --- Validators ---

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+]", password):
        raise ValueError("Password must contain a special character")
    return password
