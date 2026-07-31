from pydantic import BaseModel, Field


class TranslationOut(BaseModel):
    key: str
    en: str
    ru: str
    uz: str


class TranslationsResponse(BaseModel):
    translations: dict[str, TranslationOut]


class SyncRequest(BaseModel):
    texts: list[str] = Field(..., max_length=500, description="English UI strings to ensure exist")


class SyncResponse(BaseModel):
    translations: dict[str, TranslationOut]
