from pydantic import BaseModel
from datetime import datetime


class BrandCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    logo: str | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
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
