from pydantic import BaseModel


class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    price: float = 0
    name: str = ""
    size: str | None = None
    color: str | None = None
    barcode: str = ""

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse] = []
    total: float = 0
