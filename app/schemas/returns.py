from pydantic import BaseModel
from datetime import datetime


class ReturnItemCreate(BaseModel):
    variant_id: int
    quantity: int
    price: float = 0


class ReturnItemResponse(BaseModel):
    id: int
    return_id: int
    variant_id: int
    quantity: int
    price: float
    barcode: str = ""
    sku: str = ""

    class Config:
        from_attributes = True


class ReturnCreate(BaseModel):
    order_id: int
    reason: str | None = None
    notes: str | None = None


class ReturnConfirmResponse(BaseModel):
    id: int
    status: str
    items_count: int
    total_quantity: int
