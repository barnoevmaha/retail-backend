from pydantic import BaseModel


class SizeCreate(BaseModel):
    name: str
    sort_order: int = 0


class SizeResponse(BaseModel):
    id: int
    name: str
    sort_order: int

    class Config:
        from_attributes = True
