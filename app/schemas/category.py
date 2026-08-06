from pydantic import BaseModel
from datetime import datetime

from app.schemas.slug import SluggedBase


class CategoryCreate(SluggedBase):
    name: str
    description: str | None = None
    image: str | None = None
    sort_order: int = 0
    parent_id: int | None = None
    size_system: str | None = None


class CategoryUpdate(SluggedBase):
    name: str | None = None
    description: str | None = None
    image: str | None = None
    sort_order: int | None = None
    parent_id: int | None = None
    is_active: bool | None = None
    size_system: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image: str | None
    is_active: bool
    sort_order: int
    parent_id: int | None
    size_system: str | None = None

    class Config:
        from_attributes = True
