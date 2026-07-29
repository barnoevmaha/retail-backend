from pydantic import BaseModel
from datetime import datetime


class AdjustmentItemCreate(BaseModel):
    variant_id: int
    expected_quantity: int = 0
    actual_quantity: int = 0


class AdjustmentItemResponse(BaseModel):
    id: int
    adjustment_id: int
    variant_id: int
    expected_quantity: int
    actual_quantity: int
    difference: int
    barcode: str = ""
    sku: str = ""

    class Config:
        from_attributes = True


class AdjustmentCreate(BaseModel):
    reason: str = "inventory_count"
    notes: str | None = None


class AdjustmentConfirmResponse(BaseModel):
    id: int
    status: str
    items_count: int
    differences: list[dict]
