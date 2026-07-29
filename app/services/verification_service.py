import secrets
import time
import re
from datetime import datetime, timedelta, timezone

import bcrypt

from app.repositories.customer_repo import CustomerRepository
from app.services.email_provider import EmailProvider, MockEmailProvider
from app.services.sms_service import SmsService, MockSmsProvider
from app.core.security import hash_password, verify_password


class VerificationService:
    def __init__(self, db, email_provider: EmailProvider | None = None, sms_service: SmsService | None = None):
        self.repo = CustomerRepository(db)
        self.email_provider = email_provider or MockEmailProvider()
        self.sms_service = sms_service or SmsService(db, MockSmsProvider())
        self._rate_limits: dict[str, list[float]] = {}

    # --- Code generation ---

    def generate_code(self) -> str:
        return f"{secrets.randbelow(1000000):06d}"

    def hash_code(self, code: str) -> str:
        return hash_password(code)  # bcrypt

    def verify_code(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    # --- Rate limiting ---

    def _check_rate_limit(self, key: str, max_attempts: int = 5, window: int = 60) -> bool:
        now = time.time()
        if key not in self._rate_limits:
            self._rate_limits[key] = []
        self._rate_limits[key] = [t for t in self._rate_limits[key] if now - t < window]
        if len(self._rate_limits[key]) >= max_attempts:
            return False
        self._rate_limits[key].append(now)
        return True

    def _check_resend_limit(self, key: str) -> bool:
        return self._check_rate_limit(f"resend:{key}", max_attempts=1, window=60)

    def _check_verify_limit(self, key: str) -> bool:
        return self._check_rate_limit(f"verify:{key}", max_attempts=5, window=300)

    # --- Send verification code via email ---

    def send_email_code(self, email: str) -> str:
        if not self._check_resend_limit(email):
            raise ValueError("Please wait 60 seconds before requesting another code")
        code = self.generate_code()
        hashed = self.hash_code(code)
        customer = self.repo.get_by_email(email)
        if customer:
            self.repo.update(customer,
                email_verification_code=hashed,
                email_verification_expires=datetime.now(timezone.utc) + timedelta(minutes=10))
        self.email_provider.send(email, "Your verification code", f"Your code is: {code}")
        return code

    def send_phone_code(self, phone: str) -> str:
        if not self._check_resend_limit(phone):
            raise ValueError("Please wait 60 seconds before requesting another code")
        code = self.generate_code()
        hashed = self.hash_code(code)
        customer = self.repo.get_by_phone(phone)
        if customer:
            self.repo.update(customer,
                phone_verification_code=hashed,
                phone_verification_expires=datetime.now(timezone.utc) + timedelta(minutes=10))
        self.sms_service.send(phone, f"Your verification code is: {code}")
        return code

    def verify_email_code(self, email: str, code: str) -> bool:
        if not self._check_verify_limit(email):
            raise ValueError("Too many attempts. Try again later.")
        customer = self.repo.get_by_email(email)
        if not customer or not customer.email_verification_code:
            raise ValueError("No verification code found")
        if customer.email_verification_expires and customer.email_verification_expires < datetime.now(timezone.utc):
            raise ValueError("Verification code expired")
        if not self.verify_code(code, customer.email_verification_code):
            raise ValueError("Invalid verification code")
        self.repo.update(customer, email_verified=True, email_verification_code=None, email_verification_expires=None)
        return True

    def verify_phone_code(self, phone: str, code: str) -> bool:
        if not self._check_verify_limit(phone):
            raise ValueError("Too many attempts. Try again later.")
        customer = self.repo.get_by_phone(phone)
        if not customer or not customer.phone_verification_code:
            raise ValueError("No verification code found")
        if customer.phone_verification_expires and customer.phone_verification_expires < datetime.now(timezone.utc):
            raise ValueError("Verification code expired")
        if not self.verify_code(code, customer.phone_verification_code):
            raise ValueError("Invalid verification code")
        self.repo.update(customer, phone_verified=True, phone_verification_code=None, phone_verification_expires=None)
        return True

    # --- Forgot password flow ---

    def send_reset_code(self, identifier: str) -> str:
        customer = self.repo.get_by_email(identifier) or self.repo.get_by_phone(identifier)
        if not customer:
            raise ValueError("Account not found")
        code = self.generate_code()
        hashed = self.hash_code(code)
        self.repo.update(customer, password_reset_code=hashed, password_reset_expires=datetime.now(timezone.utc) + timedelta(minutes=10))
        if "@" in identifier:
            self.email_provider.send(identifier, "Password reset code", f"Your code is: {code}")
        else:
            self.sms_service.send(identifier, f"Your password reset code is: {code}")
        return code

    def verify_reset_code(self, identifier: str, code: str) -> bool:
        if not self._check_verify_limit(f"reset:{identifier}"):
            raise ValueError("Too many attempts. Try again later.")
        customer = self.repo.get_by_email(identifier) or self.repo.get_by_phone(identifier)
        if not customer or not customer.password_reset_code:
            raise ValueError("No reset code found")
        if customer.password_reset_expires and customer.password_reset_expires < datetime.now(timezone.utc):
            raise ValueError("Reset code expired")
        if not self.verify_code(code, customer.password_reset_code):
            raise ValueError("Invalid reset code")
        return True

    def get_customer_by_identifier(self, identifier: str):
        return self.repo.get_by_email(identifier) or self.repo.get_by_phone(identifier)
