from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.writeoff import WriteOffItem
from app.models.user import User
from app.repositories.writeoff_repo import WriteOffRepository
from app.repositories.variant_repo import VariantRepository
from app.services.stock_service import StockService


VALID_REASONS = ["damaged", "lost", "expired", "manual"]


class WriteOffService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WriteOffRepository(db)
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

    def add_item(self, writeoff_id: int, variant_id: int, quantity: int):
        writeoff = self.repo.get_by_id(writeoff_id)
        if not writeoff:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Write-off not found")
        if writeoff.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add items to draft write-offs")
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        if variant.quantity < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for variant {variant.barcode}")
        return self.repo.add_item(writeoff_id, variant_id, quantity)

    def confirm(self, writeoff_id: int, user: User):
        writeoff = self.repo.get_by_id(writeoff_id)
        if not writeoff:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Write-off not found")
        if writeoff.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Write-off already confirmed")
        items = self.db.query(WriteOffItem).filter(WriteOffItem.writeoff_id == writeoff_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items to write off")

        for item in items:
            self.stock_service.write_off(
                variant_id=item.variant_id,
                quantity=item.quantity,
                user=user,
                reason=f"Write-off #{writeoff_id}: {writeoff.reason}",
            )
        self.repo.update(writeoff, status="confirmed")
        return {
            "id": writeoff_id,
            "status": "confirmed",
            "items_count": len(items),
            "total_quantity": sum(i.quantity for i in items),
        }

    def list_all(self, skip: int = 0, limit: int = 50):
        writeoffs = self.repo.list_all(skip, limit)
        return [{
            "id": w.id,
            "reason": w.reason,
            "notes": w.notes,
            "status": w.status,
            "items_count": len(w.items),
            "created_at": w.created_at,
        } for w in writeoffs]

    def get_detail(self, writeoff_id: int):
        writeoff = self.repo.get_by_id(writeoff_id)
        if not writeoff:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Write-off not found")
        items = []
        for item in writeoff.items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            items.append({
                "id": item.id,
                "writeoff_id": item.writeoff_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "barcode": variant.barcode if variant else "",
                "sku": variant.sku if variant else "",
            })
        return {
            "id": writeoff.id,
            "reason": writeoff.reason,
            "notes": writeoff.notes,
            "status": writeoff.status,
            "items": items,
            "created_at": writeoff.created_at,
        }
