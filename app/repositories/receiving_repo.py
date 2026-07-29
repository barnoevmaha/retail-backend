from sqlalchemy.orm import Session

from app.models.receiving import Receiving, ReceivingItem


class ReceivingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Receiving | None:
        return self.db.query(Receiving).filter(Receiving.id == id).first()

    def list_all(self, status: str | None = None, skip: int = 0, limit: int = 50) -> list[Receiving]:
        query = self.db.query(Receiving)
        if status:
            query = query.filter(Receiving.status == status)
        return query.order_by(Receiving.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Receiving:
        r = Receiving(**kwargs)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def update(self, receiving: Receiving, **kwargs) -> Receiving:
        for key, value in kwargs.items():
            setattr(receiving, key, value)
        self.db.commit()
        self.db.refresh(receiving)
        return receiving

    def add_item(self, receiving_id: int, variant_id: int, quantity: int, purchase_price: float) -> ReceivingItem:
        item = ReceivingItem(receiving_id=receiving_id, variant_id=variant_id, quantity=quantity, purchase_price=purchase_price)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item(self, item: ReceivingItem):
        self.db.delete(item)
        self.db.commit()
