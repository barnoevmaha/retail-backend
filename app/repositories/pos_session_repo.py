from sqlalchemy.orm import Session

from app.models.pos_session import PosSession


class PosSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int, status: str | None = None) -> list[PosSession]:
        query = self.db.query(PosSession).filter(PosSession.user_id == user_id)
        if status:
            query = query.filter(PosSession.status == status)
        return query.order_by(PosSession.updated_at.desc()).all()

    def list_suspended(self) -> list[PosSession]:
        return self.db.query(PosSession).filter(PosSession.status == "suspended").order_by(PosSession.updated_at.desc()).all()

    def get_by_id(self, id: int) -> PosSession | None:
        return self.db.query(PosSession).filter(PosSession.id == id).first()

    def create(self, **kwargs) -> PosSession:
        s = PosSession(**kwargs)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def update(self, session_obj: PosSession, **kwargs) -> PosSession:
        for k, v in kwargs.items():
            setattr(session_obj, k, v)
        self.db.commit()
        self.db.refresh(session_obj)
        return session_obj
