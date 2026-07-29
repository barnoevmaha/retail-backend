from pydantic import BaseModel
from datetime import datetime


class PromotionCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    min_amount: float = 0
    usage_limit: int = 0
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class PromotionUpdate(BaseModel):
    discount_type: str | None = None
    discount_value: float | None = None
    min_amount: float | None = None
    usage_limit: int | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool | None = None


class PromotionResponse(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    min_amount: float
    usage_limit: int
    used_count: int
    starts_at: datetime | None
    ends_at: datetime | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
