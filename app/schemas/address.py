from pydantic import BaseModel
from datetime import datetime


class AddressCreate(BaseModel):
    country: str = ""
    region: str = ""
    city: str = ""
    street: str = ""
    house: str = ""
    apartment: str = ""
    postal_code: str = ""
    receiver_name: str
    receiver_phone: str
    is_default_shipping: bool = False
    is_default_billing: bool = False


class AddressUpdate(BaseModel):
    country: str | None = None
    region: str | None = None
    city: str | None = None
    street: str | None = None
    house: str | None = None
    apartment: str | None = None
    postal_code: str | None = None
    receiver_name: str | None = None
    receiver_phone: str | None = None
    is_default_shipping: bool | None = None
    is_default_billing: bool | None = None


class AddressResponse(BaseModel):
    id: int
    customer_id: int
    country: str | None
    region: str | None
    city: str | None
    street: str | None
    house: str | None
    apartment: str | None
    postal_code: str | None
    receiver_name: str | None
    receiver_phone: str | None
    is_default_shipping: bool
    is_default_billing: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
