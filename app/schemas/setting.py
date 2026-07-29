from pydantic import BaseModel
from datetime import datetime


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str | None

    class Config:
        from_attributes = True


class SettingUpsert(BaseModel):
    key: str
    value: str | None = None
