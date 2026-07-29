from pydantic import BaseModel
from datetime import datetime


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    text: str | None = None


class ReviewUpdate(BaseModel):
    rating: int | None = None
    text: str | None = None
    is_approved: bool | None = None


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    customer_id: int
    rating: int
    text: str | None
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
