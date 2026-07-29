from pydantic import BaseModel
from datetime import datetime


class WarehouseCreate(BaseModel):
    name: str
    address: str | None = None


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    is_active: bool | None = None


class WarehouseResponse(BaseModel):
    id: int
    name: str
    address: str | None
    is_active: bool

    class Config:
        from_attributes = True
