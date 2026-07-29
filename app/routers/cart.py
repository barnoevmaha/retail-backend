from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import optional_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.services.cart_service import CartService

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _get_cart(db, user, session_key):
    svc = CartService(db)
    customer_id = None
    if user:
        from app.repositories.customer_repo import CustomerRepository
        customer = CustomerRepository(db).get_by_user_id(user.id)
        if customer:
            customer_id = customer.id
    cart = svc.get_or_create_cart(customer_id=customer_id, session_key=session_key or None)
    return svc, cart


@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    x_session_key: str = Header(default=""),
):
    svc, cart = _get_cart(db, user, x_session_key)
    return svc._build_cart(cart.id)


@router.post("/items")
def add_to_cart(
    body: CartItemCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    x_session_key: str = Header(default=""),
):
    svc, cart = _get_cart(db, user, x_session_key)
    return svc.add_item(cart.id, body.variant_id, body.quantity)


@router.put("/items/{item_id}")
def update_cart_item(
    item_id: int,
    body: CartItemUpdate,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    x_session_key: str = Header(default=""),
):
    svc, cart = _get_cart(db, user, x_session_key)
    return svc.update_item_quantity(cart.id, item_id, body.quantity)


@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    x_session_key: str = Header(default=""),
):
    svc, cart = _get_cart(db, user, x_session_key)
    return svc.remove_item(cart.id, item_id)
