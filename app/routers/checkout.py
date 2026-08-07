from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import optional_current_customer, optional_current_user
from app.models.customer import Customer
from app.models.user import User
from app.repositories.customer_repo import CustomerRepository
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.promotion_service import PromotionService
from app.schemas.order import OrderResponse

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


class CheckoutRequest(BaseModel):
    payment_method: str = "card"
    promo_code: str | None = None
    session_key: str | None = None
    customer_id: int | None = None
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    apartment: str | None = None
    delivery_note: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@router.post("/", response_model=OrderResponse)
def checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    customer: Customer | None = Depends(optional_current_customer),
    x_session_key: str = Header(default=""),
    x_customer_id: str | None = Header(default=None),
):
    # Staff/POS sales are walk-in: no delivery fields required. Storefront checkout (customer or
    # anonymous) must always provide delivery info, so enforce it here for non-staff callers.
    is_staff = user is not None and user.role in ("super_admin", "admin", "manager", "cashier", "warehouse_employee")

    # Authenticated customer identity from JWT always wins; never trust a client-supplied customer_id.
    # X-Customer-Id is honored ONLY for staff/POS (they create orders for walk-in customers);
    # customer and anonymous callers can never attribute an order to a customer they do not own.
    customer_id = customer.id if customer else None
    if not customer_id and is_staff and x_customer_id:
        try:
            customer_id = int(x_customer_id)
        except ValueError:
            customer_id = None
    if not customer_id and is_staff:
        profile = CustomerRepository(db).get_by_user_id(user.id)
        if profile:
            customer_id = profile.id

    if not is_staff:
        missing = [f for f in ("full_name", "phone", "city", "address") if not getattr(body, f)]
        if missing:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=f"Missing required delivery fields: {', '.join(missing)}")

    cart_svc = CartService(db)
    cart = cart_svc.get_or_create_cart(
        customer_id=customer_id,
        session_key=body.session_key or x_session_key or None,
    )

    order_svc = OrderService(db)
    order = order_svc.create_from_cart(
        cart_id=cart.id,
        customer_id=customer_id,
        payment_method=body.payment_method,
        user=user,
        full_name=body.full_name,
        phone=body.phone,
        city=body.city,
        address=body.address,
        apartment=body.apartment,
        delivery_note=body.delivery_note,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    response = order_svc.build_response(order)

    if body.promo_code:
        try:
            promo_svc = PromotionService(db)
            promo_svc.validate_code(body.promo_code, float(order.total_amount))
            promo_svc.use_code(body.promo_code)
        except Exception:
            pass

    return OrderResponse.model_validate(response)
