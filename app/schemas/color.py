from pydantic import BaseModel


class ColorCreate(BaseModel):
    name: str
    hex_value: str | None = None


class ColorResponse(BaseModel):
    id: int
    name: str
    hex_value: str | None

    class Config:
        from_attributes = True
