from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pathlib import Path
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.brand_repo import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.utils.slug import unique_slug

router = APIRouter(prefix="/api/brands", tags=["brands"])

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/{brand_id}/logo", response_model=BrandResponse)
def upload_logo(
    brand_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = BrandRepository(db)
    brand = repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    ext = Path(file.filename).suffix if file.filename else ".png"
    filename = f"brand-{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / filename).write_bytes(file.file.read())
    return repo.update(brand, logo=f"/uploads/{filename}")


@router.get("/", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    return BrandRepository(db).list_all()


@router.get("/{slug}", response_model=BrandResponse)
def get_brand(slug: str, db: Session = Depends(get_db)):
    brand = BrandRepository(db).get_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


@router.post("/", response_model=BrandResponse)
def create_brand(
    body: BrandCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = BrandRepository(db)
    payload = body.model_dump()
    payload["slug"] = unique_slug(payload["slug"], lambda s: repo.get_by_slug(s) is not None)
    return repo.create(**payload)


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    body: BrandUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = BrandRepository(db)
    brand = repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    def slug_taken(s: str) -> bool:
        existing = repo.get_by_slug(s)
        return existing is not None and existing.id != brand.id

    payload = body.model_dump(exclude_unset=True)
    if payload.get("slug") is None:
        payload.pop("slug", None)
    if payload.get("slug"):
        payload["slug"] = unique_slug(payload["slug"], slug_taken)
    return repo.update(brand, **payload)


@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    repo = BrandRepository(db)
    brand = repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    repo.delete(brand)
    return {"ok": True}
