from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService

FAILED_LOGIN_LIMIT = 5
LOCKOUT_MINUTES = 15


class AuthService:
    def __init__(self, repo: UserRepository, db: Session | None = None):
        self.repo = repo
        self.db = db

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Try again later.")
        if not verify_password(password, user.password_hash):
            attempts = (user.failed_login_attempts or 0) + 1
            if attempts >= FAILED_LOGIN_LIMIT:
                lock = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                self.repo.update(user, failed_login_attempts=attempts, locked_until=lock)
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Try again later.")
            self.repo.update(user, failed_login_attempts=attempts)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        self.repo.update(user, failed_login_attempts=0, locked_until=None)
        if self.db:
            AuditService(self.db).log("login", "user", user.id, user, new_values={"email": email})
        return create_access_token({"sub": str(user.id), "role": user.role})

    def register(self, email: str, password: str, role: str = "customer") -> str:
        # role is never trusted from the client — self-registration is always a customer
        role = "customer"
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = self.repo.create(email, hash_password(password), role)
        if self.db:
            AuditService(self.db).log("create", "user", user.id, user, new_values={"email": email, "role": role})
        return create_access_token({"sub": str(user.id), "role": user.role})

    def change_password(self, user: User, current_password: str, new_password: str, confirm_password: str) -> None:
        if len(new_password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")
        if new_password == current_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from current password")
        if new_password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        user.password_hash = hash_password(new_password)
        self.repo.update(user)
        if self.db:
            AuditService(self.db).log("CHANGE_PASSWORD", "User", user.id, user)
