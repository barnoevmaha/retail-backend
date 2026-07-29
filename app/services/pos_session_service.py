from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.pos_session_repo import PosSessionRepository
from app.models.user import User


class PosSessionService:
    def __init__(self, db: Session):
        self.repo = PosSessionRepository(db)

    def suspend(self, data, user: User | None = None):
        return self.repo.create(
            user_id=user.id if user else None,
            status="suspended",
            items=data.items,
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            payment_method=data.payment_method,
            total=data.total,
        )

    def resume(self, session_id: int, user: User | None = None):
        session = self.repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if user and session.user_id and session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
        return self.repo.update(session, status="active")

    def cancel(self, session_id: int, user: User | None = None):
        session = self.repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return self.repo.update(session, status="cancelled")

    def list_suspended(self):
        return self.repo.list_suspended()

    def get(self, session_id: int):
        session = self.repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
