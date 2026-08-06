from pydantic import BaseModel
from datetime import datetime


class FavoriteResponse(BaseModel):
    id: int
    customer_id: int
    product_id: int
    created_at: datetime
    product_name: str | None = None
    product_slug: str | None = None
    image_url: str | None = None
    price: float | None = None

    class Config:
        from_attributes = True
