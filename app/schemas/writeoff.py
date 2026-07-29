from pydantic import BaseModel
from datetime import datetime


class WriteOffItemCreate(BaseModel):
    variant_id: int
    quantity: int


class WriteOffItemResponse(BaseModel):
    id: int
    writeoff_id: int
    variant_id: int
    quantity: int
    barcode: str = ""
    sku: str = ""

    class Config:
        from_attributes = True


class WriteOffCreate(BaseModel):
    reason: str = "damaged"
    notes: str | None = None


class WriteOffConfirmResponse(BaseModel):
    id: int
    status: str
    items_count: int
    total_quantity: int
