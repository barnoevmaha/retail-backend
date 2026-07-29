from sqlalchemy.orm import Session

from app.models.customer import Address


class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Address | None:
        return self.db.query(Address).filter(Address.id == id).first()

    def list_by_customer(self, customer_id: int) -> list[Address]:
        return self.db.query(Address).filter(Address.customer_id == customer_id).all()

    def create(self, **kwargs) -> Address:
        a = Address(**kwargs)
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        return a

    def update(self, address: Address, **kwargs) -> Address:
        for k, v in kwargs.items():
            setattr(address, k, v)
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete(self, address: Address):
        self.db.delete(address)
        self.db.commit()

    def clear_default_shipping(self, customer_id: int):
        self.db.query(Address).filter(
            Address.customer_id == customer_id, Address.is_default_shipping.is_(True)
        ).update({"is_default_shipping": False})

    def clear_default_billing(self, customer_id: int):
        self.db.query(Address).filter(
            Address.customer_id == customer_id, Address.is_default_billing.is_(True)
        ).update({"is_default_billing": False})
