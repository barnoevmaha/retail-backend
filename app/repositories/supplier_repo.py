from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Supplier | None:
        return self.db.query(Supplier).filter(Supplier.id == id).first()

    def list_all(self, search: str = "", skip: int = 0, limit: int = 50) -> list[Supplier]:
        query = self.db.query(Supplier)
        if search:
            q = f"%{search}%"
            query = query.filter(
                or_(
                    Supplier.company_name.ilike(q),
                    Supplier.contact_person.ilike(q),
                    Supplier.phone.ilike(q),
                    Supplier.email.ilike(q),
                    Supplier.tax_number.ilike(q),
                )
            )
        return query.offset(skip).limit(limit).all()

    def count(self, search: str = "") -> int:
        query = self.db.query(Supplier)
        if search:
            q = f"%{search}%"
            query = query.filter(
                or_(
                    Supplier.company_name.ilike(q),
                    Supplier.contact_person.ilike(q),
                    Supplier.phone.ilike(q),
                    Supplier.email.ilike(q),
                    Supplier.tax_number.ilike(q),
                )
            )
        return query.count()

    def create(self, **kwargs) -> Supplier:
        s = Supplier(**kwargs)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def update(self, supplier: Supplier, **kwargs) -> Supplier:
        for key, value in kwargs.items():
            setattr(supplier, key, value)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
