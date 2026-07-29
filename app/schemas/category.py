from pydantic import BaseModel
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    image: str | None = None
    sort_order: int = 0
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    image: str | None = None
    sort_order: int | None = None
    parent_id: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image: str | None
    is_active: bool
    sort_order: int
    parent_id: int | None

    class Config:
        from_attributes = True
