from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.product import Product
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.utils.slug import unique_slug

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/size-systems")
def list_size_systems(db: Session = Depends(get_db)):
    from app.services.size_systems import SIZE_SYSTEMS
    return [{"key": k, "sizes": sizes} for k, sizes in SIZE_SYSTEMS.items()]


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return CategoryRepository(db).list_all()


@router.get("/{slug}", response_model=CategoryResponse)
def get_category(slug: str, db: Session = Depends(get_db)):
    cat = CategoryRepository(db).get_by_slug(slug)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat


@router.post("/", response_model=CategoryResponse)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = CategoryRepository(db)
    payload = body.model_dump()
    payload["slug"] = unique_slug(payload["slug"], lambda s: repo.get_by_slug(s) is not None)
    if not payload.get("size_system"):
        from app.services.size_systems import system_for_category
        payload["size_system"] = system_for_category(payload["name"], payload["slug"])
    return repo.create(**payload)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = CategoryRepository(db)
    cat = repo.get_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    def slug_taken(s: str) -> bool:
        existing = repo.get_by_slug(s)
        return existing is not None and existing.id != cat.id

    payload = body.model_dump(exclude_unset=True)
    if payload.get("slug") is None:
        payload.pop("slug", None)
    if payload.get("slug"):
        payload["slug"] = unique_slug(payload["slug"], slug_taken)
    if "size_system" in payload and not payload.get("size_system"):
        from app.services.size_systems import system_for_category
        payload["size_system"] = system_for_category(cat.name, cat.slug)
    return repo.update(cat, **payload)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    repo = CategoryRepository(db)
    cat = repo.get_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    subtree = [cat.id] + [c.id for c in cat.children]
    if db.query(Product).filter(Product.category_id.in_(subtree)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Category cannot be deleted because it (or a subcategory) still has products.")
    repo.delete(cat)
    return {"ok": True}
