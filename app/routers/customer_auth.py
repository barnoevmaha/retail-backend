from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.models.customer import Customer
from app.schemas.customer import (
    RegisterEmailRequest, RegisterEmailVerifyRequest,
    RegisterPhoneRequest, RegisterPhoneVerifyRequest,
    CustomerLoginRequest, CustomerTokenResponse, CustomerResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
    SendCodeRequest, LinkEmailRequest, LinkEmailVerifyRequest,
    LinkPhoneRequest, LinkPhoneVerifyRequest,
)
from app.services.customer_auth_service import CustomerAuthService

router = APIRouter(prefix="/api/customer/auth", tags=["customer_auth"])


@router.post("/register/email")
def register_email_send(body: RegisterEmailRequest, db: Session = Depends(get_db)):
    return CustomerAuthService(db).register_email_send(body.first_name, body.last_name, body.email)


@router.post("/register/email/verify")
def register_email_verify(body: RegisterEmailVerifyRequest, db: Session = Depends(get_db)):
    result = CustomerAuthService(db).register_email_verify(body.email, body.code, body.password, body.confirm_password)
    result["customer"] = CustomerResponse.model_validate(result["customer"])
    return result


@router.post("/register/phone")
def register_phone_send(body: RegisterPhoneRequest, db: Session = Depends(get_db)):
    return CustomerAuthService(db).register_phone_send(body.first_name, body.last_name, body.phone)


@router.post("/register/phone/verify")
def register_phone_verify(body: RegisterPhoneVerifyRequest, db: Session = Depends(get_db)):
    result = CustomerAuthService(db).register_phone_verify(body.phone, body.code, body.password, body.confirm_password)
    result["customer"] = CustomerResponse.model_validate(result["customer"])
    return result


@router.post("/login")
def customer_login(body: CustomerLoginRequest, db: Session = Depends(get_db)):
    return CustomerAuthService(db).login(body.login, body.password)


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return CustomerAuthService(db).forgot_password(body.identifier)


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    return CustomerAuthService(db).reset_password(body.identifier, body.code, body.new_password, body.confirm_password)


# --- Link email/phone to existing account ---

@router.post("/link-email")
def link_email_send(body: LinkEmailRequest, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return CustomerAuthService(db).link_email_send(customer, body.email)


@router.post("/link-email/verify")
def link_email_verify(body: LinkEmailVerifyRequest, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return CustomerAuthService(db).link_email_verify(customer, body.email, body.code)


@router.post("/link-phone")
def link_phone_send(body: LinkPhoneRequest, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return CustomerAuthService(db).link_phone_send(customer, body.phone)


@router.post("/link-phone/verify")
def link_phone_verify(body: LinkPhoneVerifyRequest, db: Session = Depends(get_db), customer: Customer = Depends(get_current_customer)):
    return CustomerAuthService(db).link_phone_verify(customer, body.phone, body.code)
