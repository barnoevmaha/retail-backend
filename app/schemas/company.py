from pydantic import BaseModel


class CompanyResponse(BaseModel):
    id: int
    name: str
    address: str | None
    phone: str | None
    email: str | None
    logo: str | None
    tin: str | None

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    logo: str | None = None
    tin: str | None = None
