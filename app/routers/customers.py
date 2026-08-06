from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.repositories.customer_repo import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return CustomerRepository(db).list_all(skip, limit)


@router.get("/me", response_model=CustomerResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repo = CustomerRepository(db)
    customer = repo.get_by_user_id(user.id)
    if not customer:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    return customer


@router.get("/{customer_id}/detail")
def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    from fastapi import HTTPException, status
    from app.models.customer import Address as AddressModel

    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    orders = OrderService(db).list_orders(customer_id=customer_id, limit=20)
    return {
        "customer": customer,
        "addresses": db.query(AddressModel).filter(AddressModel.customer_id == customer_id).order_by(AddressModel.created_at.desc()).all(),
        "recent_orders": [OrderService(db).build_response(o) for o in orders],
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if not customer:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerResponse)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
):
    repo = CustomerRepository(db)
    if repo.get_by_phone(body.phone):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already exists")
    return repo.create(**body.model_dump())


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if not customer:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return repo.update(customer, **body.model_dump(exclude_unset=True))


@router.put("/{customer_id}/block")
def block_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if not customer:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    repo.update(customer, is_blocked=not customer.is_blocked)
    return {"message": "Customer blocked" if customer.is_blocked else "Customer unblocked", "is_blocked": customer.is_blocked}
