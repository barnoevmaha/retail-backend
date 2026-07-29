from pydantic import BaseModel
from datetime import datetime


class SupplierCreate(BaseModel):
    company_name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_number: str | None = None
    notes: str | None = None


class SupplierUpdate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tax_number: str | None = None
    notes: str | None = None


class SupplierResponse(BaseModel):
    id: int
    company_name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    tax_number: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
