from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.adjustment import AdjustmentItem
from app.models.user import User
from app.repositories.adjustment_repo import AdjustmentRepository
from app.repositories.variant_repo import VariantRepository
from app.services.stock_service import StockService


VALID_REASONS = ["inventory_count", "correction", "initial_balance"]


class AdjustmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdjustmentRepository(db)
        self.variant_repo = VariantRepository(db)
        self.stock_service = StockService(db)

    def create(self, reason: str, notes: str | None, user: User):
        if reason not in VALID_REASONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid reason. Must be one of: {', '.join(VALID_REASONS)}")
        return self.repo.create(
            user_id=user.id,
            reason=reason,
            notes=notes,
            status="draft",
        )

    def add_item(self, adjustment_id: int, variant_id: int, expected: int, actual: int):
        adj = self.repo.get_by_id(adjustment_id)
        if not adj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
        if adj.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add items to draft adjustments")
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        return self.repo.add_item(adjustment_id, variant_id, expected, actual)

    def confirm(self, adjustment_id: int, user: User):
        adj = self.repo.get_by_id(adjustment_id)
        if not adj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
        if adj.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adjustment already confirmed")
        items = self.db.query(AdjustmentItem).filter(AdjustmentItem.adjustment_id == adjustment_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items to adjust")

        differences = []
        for item in items:
            movement = self.stock_service.adjust(
                variant_id=item.variant_id,
                new_quantity=item.actual_quantity,
                user=user,
                reason=f"Adjustment #{adjustment_id}: {adj.reason}",
                comment=f"expected {item.expected_quantity}, actual {item.actual_quantity}",
            )
            differences.append({
                "variant_id": item.variant_id,
                "barcode": movement.variant.barcode if movement.variant else "",
                "expected": item.expected_quantity,
                "actual": item.actual_quantity,
                "difference": item.difference,
            })
        self.repo.update(adj, status="confirmed")
        return {
            "id": adjustment_id,
            "status": "confirmed",
            "items_count": len(items),
            "differences": differences,
        }

    def list_all(self, skip: int = 0, limit: int = 50):
        adjustments = self.repo.list_all(skip, limit)
        return [{
            "id": a.id,
            "reason": a.reason,
            "notes": a.notes,
            "status": a.status,
            "items_count": len(a.items),
            "created_at": a.created_at,
        } for a in adjustments]

    def get_detail(self, adjustment_id: int):
        adj = self.repo.get_by_id(adjustment_id)
        if not adj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
        items = []
        for item in adj.items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            items.append({
                "id": item.id,
                "adjustment_id": item.adjustment_id,
                "variant_id": item.variant_id,
                "expected_quantity": item.expected_quantity,
                "actual_quantity": item.actual_quantity,
                "difference": item.difference,
                "barcode": variant.barcode if variant else "",
                "sku": variant.sku if variant else "",
            })
        return {
            "id": adj.id,
            "reason": adj.reason,
            "notes": adj.notes,
            "status": adj.status,
            "items": items,
            "created_at": adj.created_at,
        }
