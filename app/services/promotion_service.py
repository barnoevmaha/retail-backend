from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.promotion_repo import PromotionRepository


class PromotionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PromotionRepository(db)

    def validate_code(self, code: str, order_total: float):
        promo = self.repo.get_by_code(code)
        if not promo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promo code not found")
        if not promo.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code is inactive")
        now = datetime.now(timezone.utc)
        if promo.starts_at and promo.starts_at > now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code not yet active")
        if promo.ends_at and promo.ends_at < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code has expired")
        if promo.usage_limit > 0 and promo.used_count >= promo.usage_limit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code usage limit reached")
        if order_total < promo.min_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Minimum order amount is {promo.min_amount}")

        if promo.discount_type == "percent":
            discount = order_total * float(promo.discount_value) / 100
        else:
            discount = float(promo.discount_value)

        return {"code": promo.code, "discount": round(discount, 2), "total": round(order_total - discount, 2)}

    def use_code(self, code: str):
        promo = self.repo.get_by_code(code)
        if promo:
            self.repo.update(promo, used_count=promo.used_count + 1)
