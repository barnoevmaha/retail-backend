from pydantic import BaseModel
from datetime import date, datetime


class ReceivingItemCreate(BaseModel):
    variant_id: int
    quantity: int
    purchase_price: float = 0


class ReceivingItemResponse(BaseModel):
    id: int
    receiving_id: int
    variant_id: int
    quantity: int
    purchase_price: float
    barcode: str = ""
    sku: str = ""

    class Config:
        from_attributes = True


class ReceivingCreate(BaseModel):
    supplier_id: int | None = None
    invoice_number: str | None = None
    received_date: date | None = None
    notes: str | None = None


class ReceivingStartResponse(BaseModel):
    id: int
    supplier_id: int | None
    invoice_number: str | None
    received_date: date | None
    status: str
    notes: str | None
    items: list[ReceivingItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ReceivingConfirmResponse(BaseModel):
    id: int
    status: str
    items_count: int
    total_quantity: int


class ReceivingListItem(BaseModel):
    id: int
    supplier_name: str = ""
    invoice_number: str | None
    received_date: date | None
    status: str
    items_count: int
    created_at: datetime
