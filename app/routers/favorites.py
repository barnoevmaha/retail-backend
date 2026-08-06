from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.models.customer import Customer
from app.repositories.favorite_repo import FavoriteRepository
from app.models.product import Product
from app.schemas.favorite import FavoriteResponse

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class FavoriteAdd(BaseModel):
    product_id: int


def _with_product(db, favs):
    out = []
    for f in favs:
        p = db.query(Product).filter(Product.id == f.product_id).first()
        d = FavoriteResponse.model_validate(f).model_dump()
        if p:
            d["product_name"] = p.name
            d["product_slug"] = p.slug
            d["image_url"] = p.images[0].image_url if p.images else None
            prices = [float(v.selling_price) for v in p.variants if v.selling_price is not None]
            d["price"] = min(prices) if prices else None
        out.append(d)
    return out


@router.get("/", response_model=list[FavoriteResponse])
def list_favorites(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    return _with_product(db, FavoriteRepository(db).list_by_customer(customer.id))


@router.post("/", response_model=FavoriteResponse)
def add_favorite(
    body: FavoriteAdd,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    repo = FavoriteRepository(db)
    existing = repo.get(customer.id, body.product_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in favorites")
    return repo.add(customer.id, body.product_id)


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    repo = FavoriteRepository(db)
    fav = repo.get(customer.id, product_id)
    if not fav:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in favorites")
    repo.remove(fav)
    return {"ok": True}
