from pydantic import BaseModel
from datetime import datetime


class ReceiptItemResponse(BaseModel):
    id: int
    variant_id: int | None
    product_name: str | None
    barcode: str | None
    quantity: int
    price: float

    class Config:
        from_attributes = True


class ReceiptResponse(BaseModel):
    id: int
    order_id: int | None
    receipt_number: str
    customer_name: str | None
    total_amount: float
    payment_method: str | None
    status: str
    store_name: str | None
    store_address: str | None
    store_phone: str | None
    store_tin: str | None
    created_at: datetime
    items: list[ReceiptItemResponse] = []

    class Config:
        from_attributes = True


class ReceiptListItem(BaseModel):
    id: int
    receipt_number: str
    order_id: int | None
    customer_name: str | None
    total_amount: float
    payment_method: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
