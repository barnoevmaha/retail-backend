from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, repo: UserRepository, db: Session | None = None):
        self.repo = repo
        self.db = db

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        if self.db:
            AuditService(self.db).log("login", "user", user.id, user, new_values={"email": email})
        return create_access_token({"sub": str(user.id), "role": user.role})

    def register(self, email: str, password: str, role: str = "customer") -> str:
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = self.repo.create(email, hash_password(password), role)
        if self.db:
            AuditService(self.db).log("create", "user", user.id, user, new_values={"email": email, "role": role})
        return create_access_token({"sub": str(user.id), "role": user.role})
