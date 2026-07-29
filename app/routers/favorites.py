from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.favorite_repo import FavoriteRepository
from app.repositories.customer_repo import CustomerRepository
from app.schemas.favorite import FavoriteResponse

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class FavoriteAdd(BaseModel):
    product_id: int


@router.get("/", response_model=list[FavoriteResponse])
def list_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    customer = CustomerRepository(db).get_by_user_id(user.id)
    if not customer:
        return []
    return FavoriteRepository(db).list_by_customer(customer.id)


@router.post("/", response_model=FavoriteResponse)
def add_favorite(
    body: FavoriteAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    customer = CustomerRepository(db).get_by_user_id(user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer profile required")
    repo = FavoriteRepository(db)
    existing = repo.get(customer.id, body.product_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in favorites")
    return repo.add(customer.id, body.product_id)


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    customer = CustomerRepository(db).get_by_user_id(user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer profile required")
    repo = FavoriteRepository(db)
    fav = repo.get(customer.id, product_id)
    if not fav:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in favorites")
    repo.remove(fav)
    return {"ok": True}
