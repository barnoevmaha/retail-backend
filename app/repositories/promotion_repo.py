from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.promotion import Promotion


class PromotionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Promotion | None:
        return self.db.query(Promotion).filter(Promotion.code == code).first()

    def list_active(self) -> list[Promotion]:
        now = datetime.now(timezone.utc)
        return self.db.query(Promotion).filter(
            Promotion.is_active == True,
            Promotion.starts_at <= now,
            Promotion.ends_at >= now,
        ).all()

    def list_all(self) -> list[Promotion]:
        return self.db.query(Promotion).order_by(Promotion.created_at.desc()).all()

    def create(self, **kwargs) -> Promotion:
        p = Promotion(**kwargs)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update(self, promo: Promotion, **kwargs) -> Promotion:
        for key, value in kwargs.items():
            setattr(promo, key, value)
        self.db.commit()
        self.db.refresh(promo)
        return promo
