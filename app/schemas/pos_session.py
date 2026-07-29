from pydantic import BaseModel
from datetime import datetime


class PosSessionCreate(BaseModel):
    items: str
    customer_id: int | None = None
    customer_name: str = ""
    customer_phone: str = ""
    payment_method: str = "cash"
    total: float = 0


class PosSessionUpdate(BaseModel):
    items: str | None = None
    customer_id: int | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    payment_method: str | None = None
    total: float | None = None
    status: str | None = None


class PosSessionResponse(BaseModel):
    id: int
    user_id: int | None
    status: str
    items: str
    customer_id: int | None
    customer_name: str
    customer_phone: str
    payment_method: str
    total: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
