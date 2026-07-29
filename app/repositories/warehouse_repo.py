from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Warehouse | None:
        return self.db.query(Warehouse).filter(Warehouse.id == id).first()

    def list_all(self, active_only: bool = True) -> list[Warehouse]:
        query = self.db.query(Warehouse)
        if active_only:
            query = query.filter(Warehouse.is_active == True)
        return query.all()

    def create(self, **kwargs) -> Warehouse:
        w = Warehouse(**kwargs)
        self.db.add(w)
        self.db.commit()
        self.db.refresh(w)
        return w

    def update(self, w: Warehouse, **kwargs) -> Warehouse:
        for key, value in kwargs.items():
            setattr(w, key, value)
        self.db.commit()
        self.db.refresh(w)
        return w
