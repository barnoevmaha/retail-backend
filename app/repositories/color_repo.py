from sqlalchemy.orm import Session

from app.models.color import Color


class ColorRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Color]:
        return self.db.query(Color).order_by(Color.name).all()

    def get_by_id(self, id: int) -> Color | None:
        return self.db.query(Color).filter(Color.id == id).first()

    def create(self, name: str, hex_value: str | None = None) -> Color:
        c = Color(name=name, hex_value=hex_value)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c
