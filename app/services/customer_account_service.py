from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.repositories.address_repo import AddressRepository


class CustomerAccountService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.addr_repo = AddressRepository(db)

    def get_profile(self, customer: Customer) -> Customer:
        return customer

    def update_profile(self, customer: Customer, **kwargs) -> Customer:
        return self.repo.update(customer, **kwargs)

    def list_addresses(self, customer: Customer):
        return self.addr_repo.list_by_customer(customer.id)

    def create_address(self, customer: Customer, **kwargs):
        return self.addr_repo.create(customer_id=customer.id, **kwargs)

    def update_address(self, customer: Customer, address_id: int, **kwargs):
        address = self.addr_repo.get_by_id(address_id)
        if not address or address.customer_id != customer.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        if kwargs.get("is_default_shipping"):
            self.addr_repo.clear_default_shipping(customer.id)
        if kwargs.get("is_default_billing"):
            self.addr_repo.clear_default_billing(customer.id)
        return self.addr_repo.update(address, **kwargs)

    def delete_address(self, customer: Customer, address_id: int):
        address = self.addr_repo.get_by_id(address_id)
        if not address or address.customer_id != customer.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        self.addr_repo.delete(address)
