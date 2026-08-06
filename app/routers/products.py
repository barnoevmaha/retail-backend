from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.product_image import ProductImageResponse
from app.services.product_service import ProductService
from app.repositories.product_image_repo import ProductImageRepository

router = APIRouter(prefix="/api/products", tags=["products"])


def _with_color_info(d: dict, p) -> dict:
    hex_by_id = {v.id: v.color_rel.hex_value if v.color_rel else None for v in p.variants}
    name_by_id = {v.id: v.color_rel.name if v.color_rel else None for v in p.variants}
    for vd in d["variants"]:
        vd["color_hex"] = hex_by_id.get(vd["id"])
        vd["color_name"] = vd.get("color_name") or name_by_id.get(vd["id"])
    return d


@router.get("/")
def list_products(
    q: str = "",
    category_id: int | None = Query(None),
    brand_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.models.category import Category
    from app.models.brand import Brand
    service = ProductService(db)
    products, total = service.search_products(q, category_id, brand_id, is_active, skip, limit)
    items = []
    images_repo = ProductImageRepository(db)
    for p in products:
        d = ProductResponse.model_validate(p).model_dump()
        cat = db.query(Category).filter(Category.id == p.category_id).first()
        brd = db.query(Brand).filter(Brand.id == p.brand_id).first()
        d["category_name"] = cat.name if cat else None
        d["category_slug"] = cat.slug if cat else None
        d["brand_name"] = brd.name if brd else None
        d["images"] = [ProductImageResponse.model_validate(i) for i in images_repo.list_by_product(p.id)]
        d["variants"] = [v for v in d["variants"] if v.get("is_active", True)]
        _with_color_info(d, p)
        items.append(d)
    return {"items": items, "total": total}


@router.get("/{slug}", response_model=ProductResponse)
def get_product(slug: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    p = service.get_product(slug)
    d = ProductResponse.model_validate(p).model_dump()
    d["images"] = [ProductImageResponse.model_validate(i) for i in ProductImageRepository(db).list_by_product(p.id)]
    d["variants"] = [v for v in d["variants"] if v.get("is_active", True)]
    _with_color_info(d, p)
    if p.category:
        d["category_name"] = p.category.name
        d["category_slug"] = p.category.slug
    return d


@router.post("/", response_model=ProductResponse)
def create_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = ProductService(db)
    return service.create_product(body, user)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = ProductService(db)
    return service.update_product(product_id, body, user)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin")),
):
    service = ProductService(db)
    service.delete_product(product_id, user)
    return {"ok": True}
