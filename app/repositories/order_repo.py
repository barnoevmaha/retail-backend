from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Order | None:
        return self.db.query(Order).filter(Order.id == id).first()

    def list_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> list[Order]:
        return (
            self.db.query(Order)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_all(self, status: str | None = None, skip: int = 0, limit: int = 50) -> list[Order]:
        query = self.db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(Order).count()

    def revenue(self) -> float:
        result = self.db.query(func.sum(Order.total_amount)).filter(
            Order.status.in_(["delivered", "ready"])
        ).scalar()
        return float(result or 0)

    def create(self, **kwargs) -> Order:
        order = Order(**kwargs)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def add_item(self, order_id: int, variant_id: int, quantity: int, price: float) -> OrderItem:
        item = OrderItem(order_id=order_id, variant_id=variant_id, quantity=quantity, price=price)
        self.db.add(item)
        self.db.commit()
        return item

    def update_status(self, order: Order, status: str) -> Order:
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order
