from sqlalchemy.orm import Session

from app.models.adjustment import InventoryAdjustment, AdjustmentItem


class AdjustmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> InventoryAdjustment | None:
        return self.db.query(InventoryAdjustment).filter(InventoryAdjustment.id == id).first()

    def list_all(self, skip: int = 0, limit: int = 50) -> list[InventoryAdjustment]:
        return self.db.query(InventoryAdjustment).order_by(InventoryAdjustment.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> InventoryAdjustment:
        a = InventoryAdjustment(**kwargs)
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        return a

    def update(self, adj: InventoryAdjustment, **kwargs) -> InventoryAdjustment:
        for key, value in kwargs.items():
            setattr(adj, key, value)
        self.db.commit()
        self.db.refresh(adj)
        return adj

    def add_item(self, adjustment_id: int, variant_id: int, expected: int, actual: int) -> AdjustmentItem:
        item = AdjustmentItem(
            adjustment_id=adjustment_id,
            variant_id=variant_id,
            expected_quantity=expected,
            actual_quantity=actual,
            difference=actual - expected,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
