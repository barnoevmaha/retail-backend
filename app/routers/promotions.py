from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.promotion import Promotion
from app.repositories.promotion_repo import PromotionRepository
from app.schemas.promotion import PromotionCreate, PromotionUpdate, PromotionResponse
from app.services.promotion_service import PromotionService

router = APIRouter(prefix="/api/promotions", tags=["promotions"])


class ValidateRequest(BaseModel):
    code: str
    order_total: float = 0


@router.post("/validate")
def validate_promo(body: ValidateRequest, db: Session = Depends(get_db)):
    return PromotionService(db).validate_code(body.code, body.order_total)


@router.get("/", response_model=list[PromotionResponse])
def list_promotions(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    return PromotionRepository(db).list_all()


@router.post("/", response_model=PromotionResponse)
def create_promotion(
    body: PromotionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return PromotionRepository(db).create(**body.model_dump())


@router.put("/{promo_id}", response_model=PromotionResponse)
def update_promotion(
    promo_id: int,
    body: PromotionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    repo = PromotionRepository(db)
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    return repo.update(promo, **body.model_dump(exclude_unset=True))
