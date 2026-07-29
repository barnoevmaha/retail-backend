from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement


class StockMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_variant(self, variant_id: int, skip: int = 0, limit: int = 50) -> list[StockMovement]:
        return (
            self.db.query(StockMovement)
            .filter(StockMovement.variant_id == variant_id)
            .order_by(StockMovement.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_all(self, operation: str | None = None, skip: int = 0, limit: int = 50) -> list[StockMovement]:
        query = self.db.query(StockMovement)
        if operation:
            query = query.filter(StockMovement.operation == operation)
        return (
            query.order_by(StockMovement.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, movement_id: int) -> StockMovement | None:
        return self.db.query(StockMovement).filter(StockMovement.id == movement_id).first()

    def create(self, **kwargs) -> StockMovement:
        m = StockMovement(**kwargs)
        self.db.add(m)
        self.db.flush()
        self.db.refresh(m)
        return m
