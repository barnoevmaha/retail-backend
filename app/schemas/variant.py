from pydantic import BaseModel
from datetime import datetime


class VariantCreate(BaseModel):
    product_id: int
    barcode: str = ""
    sku: str = ""
    color_id: int | None = None
    size_id: int | None = None
    size: str | None = None
    color: str | None = None
    purchase_price: float = 0
    selling_price: float = 0


class VariantUpdate(BaseModel):
    barcode: str | None = None
    sku: str | None = None
    color_id: int | None = None
    size_id: int | None = None
    size: str | None = None
    color: str | None = None
    purchase_price: float | None = None
    selling_price: float | None = None
    is_active: bool | None = None


class VariantResponse(BaseModel):
    id: int
    product_id: int
    barcode: str
    sku: str
    color_id: int | None
    size_id: int | None
    size: str | None
    color: str | None
    purchase_price: float
    selling_price: float
    quantity: int
    is_active: bool
    created_at: datetime
    color_name: str | None = None
    size_name: str | None = None
    color_hex: str | None = None

    class Config:
        from_attributes = True


class PublicVariantResponse(BaseModel):
    """Customer-facing variant view — never includes internal purchase_price."""
    id: int
    product_id: int
    barcode: str
    sku: str
    color_id: int | None
    size_id: int | None
    size: str | None
    color: str | None
    selling_price: float
    quantity: int
    is_active: bool
    created_at: datetime
    color_name: str | None = None
    size_name: str | None = None
    color_hex: str | None = None

    class Config:
        from_attributes = True
