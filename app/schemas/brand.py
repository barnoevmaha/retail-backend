from pydantic import BaseModel
from datetime import datetime

from app.schemas.slug import SluggedBase


class BrandCreate(SluggedBase):
    name: str
    description: str | None = None
    logo: str | None = None


class BrandUpdate(SluggedBase):
    name: str | None = None
    description: str | None = None
    logo: str | None = None
    is_active: bool | None = None


class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    logo: str | None
    is_active: bool

    class Config:
        from_attributes = True
