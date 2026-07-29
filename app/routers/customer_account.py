from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse, CustomerProfileUpdate
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.customer_account_service import CustomerAccountService

router = APIRouter(prefix="/api/customer/account", tags=["customer_account"])


@router.get("/me", response_model=CustomerResponse)
def get_profile(customer: Customer = Depends(get_current_customer)):
    return customer


@router.put("/me", response_model=CustomerResponse)
def update_profile(
    body: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    return CustomerAccountService(db).update_profile(customer, **body.model_dump(exclude_unset=True))


# --- Addresses ---

@router.get("/addresses", response_model=list[AddressResponse])
def list_addresses(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    return CustomerAccountService(db).list_addresses(customer)


@router.post("/addresses", response_model=AddressResponse)
def create_address(
    body: AddressCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    return CustomerAccountService(db).create_address(customer, **body.model_dump())


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    body: AddressUpdate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    return CustomerAccountService(db).update_address(customer, address_id, **body.model_dump(exclude_unset=True))


@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    CustomerAccountService(db).delete_address(customer, address_id)
    return {"message": "Address deleted"}
