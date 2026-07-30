from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
def list_products(
    q: str = "",
    category_id: int | None = Query(None),
    brand_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.models.category import Category
    from app.models.brand import Brand
    service = ProductService(db)
    products, total = service.search_products(q, category_id, brand_id, skip, limit)
    items = []
    for p in products:
        d = ProductResponse.model_validate(p).model_dump()
        cat = db.query(Category).filter(Category.id == p.category_id).first()
        brd = db.query(Brand).filter(Brand.id == p.brand_id).first()
        d["category_name"] = cat.name if cat else None
        d["brand_name"] = brd.name if brd else None
        items.append(d)
    return {"items": items, "total": total}


@router.get("/{slug}", response_model=ProductResponse)
def get_product(slug: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product(slug)


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
