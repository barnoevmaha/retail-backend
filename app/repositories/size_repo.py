from sqlalchemy.orm import Session

from app.models.size import Size


class SizeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Size]:
        return self.db.query(Size).order_by(Size.sort_order).all()

    def get_by_id(self, id: int) -> Size | None:
        return self.db.query(Size).filter(Size.id == id).first()

    def create(self, name: str, sort_order: int = 0) -> Size:
        s = Size(name=name, sort_order=sort_order)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s
