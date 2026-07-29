from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.returns import ReturnItem
from app.models.user import User
from app.repositories.return_repo import ReturnRepository
from app.repositories.variant_repo import VariantRepository
from app.repositories.order_repo import OrderRepository
from app.services.stock_service import StockService


class ReturnService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReturnRepository(db)
        self.variant_repo = VariantRepository(db)
        self.order_repo = OrderRepository(db)
        self.stock_service = StockService(db)

    def create(self, order_id: int, reason: str | None, notes: str | None, user: User):
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return self.repo.create(
            order_id=order_id,
            customer_id=order.customer_id,
            user_id=user.id,
            reason=reason,
            notes=notes,
            status="draft",
        )

    def add_item(self, return_id: int, variant_id: int, quantity: int, price: float):
        return_ = self.repo.get_by_id(return_id)
        if not return_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        if return_.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add items to draft returns")
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        return self.repo.add_item(return_id, variant_id, quantity, price)

    def confirm(self, return_id: int, user: User):
        return_ = self.repo.get_by_id(return_id)
        if not return_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        if return_.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return already confirmed")
        items = self.db.query(ReturnItem).filter(ReturnItem.return_id == return_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items to return")

        for item in items:
            self.stock_service.record_movement(
                variant_id=item.variant_id,
                operation="return",
                quantity=item.quantity,
                user=user,
                reference_type="return",
                reference_id=return_id,
                reason=f"Return #{return_id} from Order #{return_.order_id}",
            )
        self.repo.update(return_, status="confirmed")
        return {
            "id": return_id,
            "status": "confirmed",
            "items_count": len(items),
            "total_quantity": sum(i.quantity for i in items),
        }

    def cancel(self, return_id: int):
        return_ = self.repo.get_by_id(return_id)
        if not return_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        if return_.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only cancel draft returns")
        return self.repo.update(return_, status="cancelled")

    def list_all(self, status: str | None = None, skip: int = 0, limit: int = 50):
        returns = self.repo.list_all(status, skip, limit)
        result = []
        for r in returns:
            result.append({
                "id": r.id,
                "order_id": r.order_id,
                "reason": r.reason,
                "status": r.status,
                "items_count": len(r.items),
                "created_at": r.created_at,
            })
        return result

    def get_detail(self, return_id: int):
        return_ = self.repo.get_by_id(return_id)
        if not return_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        items = []
        for item in return_.items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            items.append({
                "id": item.id,
                "return_id": item.return_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": float(item.price),
                "barcode": variant.barcode if variant else "",
                "sku": variant.sku if variant else "",
            })
        return {
            "id": return_.id,
            "order_id": return_.order_id,
            "customer_id": return_.customer_id,
            "reason": return_.reason,
            "notes": return_.notes,
            "status": return_.status,
            "items": items,
            "created_at": return_.created_at,
        }
