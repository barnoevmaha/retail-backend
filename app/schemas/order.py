from pydantic import BaseModel
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    price: float
    product_name: str = ""
    product_slug: str = ""
    image_url: str = ""
    size: str | None = None
    color: str | None = None
    color_hex: str | None = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_id: int | None
    status: str
    total_amount: float
    payment_method: str | None
    payment_status: str | None
    notes: str | None
    customer_name: str | None = None
    customer_phone: str | None = None
    city: str | None = None
    address: str | None = None
    apartment: str | None = None
    delivery_note: str | None = None
    delivery_fee: float = 0
    discount: float = 0
    promo_code: str | None = None
    subtotal: float = 0
    shipping: float = 0
    items_count: int = 0
    delivery: list[str] = []
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
