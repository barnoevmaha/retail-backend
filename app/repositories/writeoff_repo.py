from sqlalchemy.orm import Session

from app.models.writeoff import WriteOff, WriteOffItem


class WriteOffRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> WriteOff | None:
        return self.db.query(WriteOff).filter(WriteOff.id == id).first()

    def list_all(self, skip: int = 0, limit: int = 50) -> list[WriteOff]:
        return self.db.query(WriteOff).order_by(WriteOff.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> WriteOff:
        w = WriteOff(**kwargs)
        self.db.add(w)
        self.db.commit()
        self.db.refresh(w)
        return w

    def update(self, writeoff: WriteOff, **kwargs) -> WriteOff:
        for key, value in kwargs.items():
            setattr(writeoff, key, value)
        self.db.commit()
        self.db.refresh(writeoff)
        return writeoff

    def add_item(self, writeoff_id: int, variant_id: int, quantity: int) -> WriteOffItem:
        item = WriteOffItem(writeoff_id=writeoff_id, variant_id=variant_id, quantity=quantity)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
