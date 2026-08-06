from pydantic import BaseModel


class ProductImageCreate(BaseModel):
    image_url: str
    sort_order: int = 0
    is_main: bool = False
    color_id: int | None = None


class ProductImageUpdate(BaseModel):
    is_main: bool | None = None
    sort_order: int | None = None
    color_id: int | None = None


class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    color_id: int | None
    image_url: str
    sort_order: int
    is_main: bool

    class Config:
        from_attributes = True
