from pydantic import BaseModel, field_validator, model_validator

from app.utils.slug import MAX_SLUG_LEN, slugify


def _checked(slug: str) -> str:
    slug = slugify(slug)
    if not slug:
        raise ValueError("slug must contain at least one letter or digit")
    if len(slug) > MAX_SLUG_LEN:
        raise ValueError(f"slug must be at most {MAX_SLUG_LEN} characters")
    return slug


class SluggedBase(BaseModel):
    """slug: optional; blank -> generated from name; always normalized + length-checked."""

    slug: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _generate_from_name(cls, data):
        if isinstance(data, dict):
            slug = data.get("slug")
            name = data.get("name")
            if (slug is None or not str(slug).strip()) and name:
                data["slug"] = name
        return data

    @field_validator("slug")
    @classmethod
    def _normalize_slug(cls, v):
        if v is None or not str(v).strip():
            return None
        return _checked(v)
