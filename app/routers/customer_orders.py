from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.models.customer import Customer
from app.schemas.order import OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/customer/orders", tags=["customer_orders"])


@router.get("/", response_model=list[OrderResponse])
def list_customer_orders(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    svc = OrderService(db)
    orders = svc.order_repo.list_by_customer(customer.id)
    return [svc.build_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def customer_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    svc = OrderService(db)
    order = svc.get_order(order_id)
    if order.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return svc.build_response(order)