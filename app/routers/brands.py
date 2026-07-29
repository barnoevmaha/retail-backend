from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.brand_repo import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse

router = APIRouter(prefix="/api/brands", tags=["brands"])


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
    if repo.get_by_slug(body.slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    return repo.create(**body.model_dump())


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
    return repo.update(brand, **body.model_dump(exclude_unset=True))


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
