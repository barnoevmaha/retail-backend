from pydantic import BaseModel
from datetime import datetime


class StockMovementCreate(BaseModel):
    variant_id: int
    warehouse_id: int | None = None
    operation: str
    quantity: int
    reference_type: str | None = None
    reference_id: int | None = None
    document_number: str | None = None
    reason: str | None = None
    comment: str | None = None


class StockMovementResponse(BaseModel):
    id: int
    variant_id: int
    warehouse_id: int | None
    user_id: int | None
    operation: str
    quantity: int
    reference_type: str | None
    reference_id: int | None
    document_number: str | None
    reason: str | None
    comment: str | None
    performed_by_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
