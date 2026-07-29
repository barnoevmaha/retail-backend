from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.receipt import Receipt, ReceiptItem


class ReceiptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Receipt | None:
        return self.db.query(Receipt).filter(Receipt.id == id).first()

    def get_by_order_id(self, order_id: int) -> Receipt | None:
        return self.db.query(Receipt).filter(Receipt.order_id == order_id).first()

    def list_all(self, skip: int = 0, limit: int = 50) -> list[Receipt]:
        return self.db.query(Receipt).order_by(desc(Receipt.created_at)).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Receipt:
        r = Receipt(**kwargs)
        self.db.add(r)
        self.db.flush()
        return r

    def add_item(self, receipt_id: int, variant_id: int | None, product_name: str | None, barcode: str | None, quantity: int, price: float) -> ReceiptItem:
        item = ReceiptItem(receipt_id=receipt_id, variant_id=variant_id, product_name=product_name, barcode=barcode, quantity=quantity, price=price)
        self.db.add(item)
        self.db.flush()
        return item
