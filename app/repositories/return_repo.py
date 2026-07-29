from sqlalchemy.orm import Session

from app.models.returns import Return, ReturnItem


class ReturnRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Return | None:
        return self.db.query(Return).filter(Return.id == id).first()

    def list_all(self, status: str | None = None, skip: int = 0, limit: int = 50) -> list[Return]:
        query = self.db.query(Return)
        if status:
            query = query.filter(Return.status == status)
        return query.order_by(Return.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Return:
        r = Return(**kwargs)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def update(self, return_: Return, **kwargs) -> Return:
        for key, value in kwargs.items():
            setattr(return_, key, value)
        self.db.commit()
        self.db.refresh(return_)
        return return_

    def add_item(self, return_id: int, variant_id: int, quantity: int, price: float) -> ReturnItem:
        item = ReturnItem(return_id=return_id, variant_id=variant_id, quantity=quantity, price=price)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
