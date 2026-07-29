from pydantic import BaseModel
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    price: float

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
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
