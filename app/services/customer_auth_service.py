from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.services.audit_service import AuditService
from app.services.verification_service import VerificationService
from app.services.email_provider import EmailProvider
from app.services.sms_service import SmsService
from app.services.provider_factory import get_email_provider, get_sms_service
from app.schemas.customer import validate_password


class CustomerAuthService:
    def __init__(self, db: Session, email_provider: EmailProvider | None = None, sms_service: SmsService | None = None):
        self.repo = CustomerRepository(db)
        self.db = db
        self.audit = AuditService(db)
        self.verification = VerificationService(db, email_provider, sms_service)

    @staticmethod
    def _validate_password(password: str) -> None:
        try:
            validate_password(password)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def _token(self, customer: Customer) -> str:
        return create_access_token({"sub": f"customer_{customer.id}", "role": "customer"})

    def _refresh_token(self, customer: Customer) -> str:
        return create_refresh_token({"sub": f"customer_{customer.id}", "role": "customer"})

    def _tokens(self, customer: Customer) -> dict:
        return {"access_token": self._token(customer), "refresh_token": self._refresh_token(customer), "token_type": "bearer"}

    def refresh_access(self, refresh_token: str) -> dict:
        payload = decode_access_token(refresh_token)
        if payload is None or payload.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        sub = payload.get("sub", "")
        if not sub.startswith("customer_"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        customer = self.repo.get_by_id(int(sub.removeprefix("customer_")))
        if not customer or customer.is_blocked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Customer not found")
        return self._tokens(customer)

    def _login_guard(self, customer: Customer):
        if customer.is_blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is blocked")
        if customer.locked_until and customer.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account is locked. Try again later.")
        if not customer.password_hash:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No password set. Use social login.")

    def register_email_send(self, first_name: str, last_name: str, email: str):
        existing = self.repo.get_by_email(email)
        if existing and existing.email_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        is_resend = existing is not None
        if not is_resend:
            self.repo.create(first_name=first_name, last_name=last_name, email=email)
        try:
            self.verification.send_email_code(email)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if is_resend:
            return {"message": "A new verification code has been sent."}
        return {"message": "Registration successful. We've sent a verification code to your email."}

    def register_email_verify(self, email: str, code: str, password: str, confirm_password: str):
        if password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        self._validate_password(password)
        customer = self.repo.get_by_email(email)
        if not customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No registration found for this email")
        try:
            self.verification.verify_email_code(email, code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        self.repo.update(customer, password_hash=hash_password(password))
        self.audit.log("REGISTER", "Customer", customer.id, None, new_values={"email": email})
        return self._tokens(customer) | {"customer": customer}

    def register_phone_send(self, first_name: str, last_name: str, phone: str):
        existing = self.repo.get_by_phone(phone)
        if existing and existing.phone_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")
        is_resend = existing is not None
        if not is_resend:
            self.repo.create(first_name=first_name, last_name=last_name, phone=phone)
        try:
            self.verification.send_phone_code(phone)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if is_resend:
            return {"message": "A new verification code has been sent."}
        return {"message": "Registration successful. We've sent a verification code to your phone."}

    def register_phone_verify(self, phone: str, code: str, password: str, confirm_password: str):
        if password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        self._validate_password(password)
        customer = self.repo.get_by_phone(phone)
        if not customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No registration found for this phone")
        try:
            self.verification.verify_phone_code(phone, code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        self.repo.update(customer, password_hash=hash_password(password))
        self.audit.log("REGISTER", "Customer", customer.id, None, new_values={"phone": phone})
        return self._tokens(customer) | {"customer": customer}

    def login(self, login: str, password: str):
        if "@" in login:
            customer = self.repo.get_by_email(login)
        else:
            customer = self.repo.get_by_phone(login)
        if not customer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        self._login_guard(customer)
        if not verify_password(password, customer.password_hash):
            attempts = (customer.failed_login_attempts or 0) + 1
            lock = None
            if attempts >= 5:
                lock = datetime.now(timezone.utc) + timedelta(minutes=15)
            self.repo.update(customer, failed_login_attempts=attempts, locked_until=lock)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        self.repo.update(customer, last_login=datetime.now(timezone.utc), failed_login_attempts=0, locked_until=None)
        self.audit.log("LOGIN", "Customer", customer.id, None, new_values={"login": login})
        return self._tokens(customer) | {"customer": customer}

    def forgot_password(self, identifier: str):
        customer = self.repo.get_by_email(identifier) or self.repo.get_by_phone(identifier)
        if not customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not found")
        try:
            self.verification.send_reset_code(identifier)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": "Reset code sent"}

    def reset_password(self, identifier: str, code: str, new_password: str, confirm_password: str):
        if new_password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        self._validate_password(new_password)
        if not self.verification.verify_reset_code(identifier, code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")
        customer = self.verification.get_customer_by_identifier(identifier)
        self.repo.update(customer, password_hash=hash_password(new_password), password_reset_code=None, password_reset_expires=None)
        self.audit.log("RESET_PASSWORD", "Customer", customer.id, None, new_values={"identifier": identifier})
        return {"message": "Password reset successfully"}

    def link_email_send(self, customer: Customer, email: str):
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        self.repo.update(customer, email=email)
        try:
            self.verification.send_email_code(email)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": "Verification code sent to email"}

    def link_email_verify(self, customer: Customer, email: str, code: str):
        try:
            self.verification.verify_email_code(email, code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        self.audit.log("VERIFY_EMAIL", "Customer", customer.id, None, new_values={"email": email})
        return {"message": "Email linked successfully"}

    def link_phone_send(self, customer: Customer, phone: str):
        if self.repo.get_by_phone(phone):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already in use")
        self.repo.update(customer, phone=phone)
        try:
            self.verification.send_phone_code(phone)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": "Verification code sent to phone"}

    def link_phone_verify(self, customer: Customer, phone: str, code: str):
        try:
            self.verification.verify_phone_code(phone, code)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        self.audit.log("VERIFY_PHONE", "Customer", customer.id, None, new_values={"phone": phone})
        return {"message": "Phone linked successfully"}
