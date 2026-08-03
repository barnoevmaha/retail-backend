from pydantic import BaseModel
from datetime import datetime

from app.schemas.slug import SluggedBase
from app.schemas.variant import VariantResponse
from app.schemas.product_image import ProductImageResponse


class ProductCreate(SluggedBase):
    name: str
    description: str | None = None
    brand_id: int | None = None
    category_id: int | None = None


class ProductUpdate(SluggedBase):
    name: str | None = None
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
    category_name: str | None = None
    brand_name: str | None = None
    variants: list[VariantResponse] = []
    images: list[ProductImageResponse] = []
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
