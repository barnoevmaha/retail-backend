from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.variant import ProductVariant
from app.repositories.variant_repo import VariantRepository
from app.schemas.variant import VariantCreate, VariantUpdate, VariantResponse
from app.services.product_service import ProductService


def _enrich(variant):
    resp = VariantResponse.model_validate(variant)
    if variant.color_rel:
        resp.color_name = variant.color_rel.name
    if variant.size_rel:
        resp.size_name = variant.size_rel.name
    return resp


router = APIRouter(prefix="/api/variants", tags=["variants"])


@router.get("/")
def list_variants(
    product_id: int | None = Query(None),
    q: str = "",
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = VariantRepository(db)
    if q:
        variants = repo.search(q, skip, limit)
    elif product_id:
        variants = repo.list_by_product(product_id)
    else:
        variants = repo.search("", skip, limit)
    return {"items": [_enrich(v) for v in variants]}


@router.get("/barcode/{barcode}")
def get_by_barcode(barcode: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    variant = service.get_variant_by_barcode(barcode)
    return _enrich(variant)


@router.get("/{variant_id}")
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    repo = VariantRepository(db)
    variant = repo.get_by_id(variant_id)
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    return _enrich(variant)


@router.delete("/{variant_id}")
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = ProductService(db)
    service.deactivate_variant(variant_id, user)
    return {"ok": True}


@router.post("/")
def create_variant(
    body: VariantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    service = ProductService(db)
    return _enrich(service.create_variant(body, user))


@router.put("/{variant_id}")
def update_variant(
    variant_id: int,
    body: VariantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = ProductService(db)
    return _enrich(service.update_variant(variant_id, body, user))
