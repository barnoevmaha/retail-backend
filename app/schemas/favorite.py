from pydantic import BaseModel
from datetime import datetime


class FavoriteResponse(BaseModel):
    id: int
    customer_id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True
