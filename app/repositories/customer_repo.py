from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id == id).first()

    def get_by_phone(self, phone: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.phone == phone).first()

    def get_by_user_id(self, user_id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.user_id == user_id).first()

    def list_all(self, skip: int = 0, limit: int = 50) -> list[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Customer:
        c = Customer(**kwargs)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c

    def update(self, customer: Customer, **kwargs) -> Customer:
        for key, value in kwargs.items():
            setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer
