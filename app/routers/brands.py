from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.brand_repo import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.utils.slug import unique_slug
from app.utils.uploads import save_uploaded_image

router = APIRouter(prefix="/api/brands", tags=["brands"])


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
    logo = save_uploaded_image(file)
    return repo.update(brand, logo=logo)


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
