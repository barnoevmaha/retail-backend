from pydantic import BaseModel
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    brand_id: int | None = None
    category_id: int | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    brand_id: int | None = None
    category_id: int | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    brand_id: int | None
    category_id: int | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
