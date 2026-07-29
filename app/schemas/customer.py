from pydantic import BaseModel
from datetime import date, datetime


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    birthday: date | None = None


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    birthday: date | None = None


class CustomerResponse(BaseModel):
    id: int
    user_id: int | None
    first_name: str
    last_name: str
    phone: str
    birthday: date | None
    total_purchases: int
    total_spent: float
    loyalty_level: str
    bonus_points: int
    created_at: datetime

    class Config:
        from_attributes = True
