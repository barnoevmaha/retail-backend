from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.stock_repo import StockMovementRepository
from app.repositories.variant_repo import VariantRepository
from app.repositories.warehouse_repo import WarehouseRepository
from app.models.user import User
from app.services.audit_service import AuditService


OPERATION_TYPES = {"receiving", "sale", "return", "write_off", "adjustment", "transfer"}


class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockMovementRepository(db)
        self.variant_repo = VariantRepository(db)
        self.warehouse_repo = WarehouseRepository(db)
        self.audit = AuditService(db)

    def record_movement(
        self,
        variant_id: int,
        operation: str,
        quantity: int,
        user: User,
        warehouse_id: int | None = None,
        reference_type: str | None = None,
        reference_id: int | None = None,
        document_number: str | None = None,
        reason: str | None = None,
        comment: str | None = None,
    ):
        if operation not in OPERATION_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid operation: {operation}")

        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

        if warehouse_id:
            warehouse = self.warehouse_repo.get_by_id(warehouse_id)
            if not warehouse:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

        if operation == "receiving":
            variant.quantity += quantity
        elif operation in ("sale", "write_off"):
            if variant.quantity < quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
            variant.quantity -= quantity
            quantity = -quantity
        elif operation == "return":
            variant.quantity += quantity
        elif operation == "adjustment":
            diff = quantity - variant.quantity
            variant.quantity = quantity
            quantity = diff
        elif operation == "transfer":
            if variant.quantity < quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
            variant.quantity -= quantity
            quantity = -quantity

        movement = self.stock_repo.create(
            variant_id=variant_id,
            warehouse_id=warehouse_id,
            user_id=user.id,
            operation=operation,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            document_number=document_number,
            reason=reason,
            comment=comment,
            performed_by_name=user.email if user else None,
        )

        self.audit.log("inventory_change", "variant", variant_id, user,
                       old_values={"operation": operation},
                       new_values={"quantity": variant.quantity, "change": quantity})

        return movement

    def receive(self, variant_id: int, quantity: int, warehouse_id: int | None, user: User, reason: str | None = None, document_number: str | None = None):
        return self.record_movement(
            variant_id=variant_id,
            operation="receiving",
            quantity=quantity,
            warehouse_id=warehouse_id,
            user=user,
            reason=reason,
            document_number=document_number,
            reference_type="receiving",
        )

    def sale(self, variant_id: int, quantity: int, user: User, order_id: int | None = None):
        return self.record_movement(
            variant_id=variant_id,
            operation="sale",
            quantity=quantity,
            user=user,
            reference_type="order",
            reference_id=order_id,
        )

    def write_off(self, variant_id: int, quantity: int, user: User, reason: str, document_number: str | None = None):
        return self.record_movement(
            variant_id=variant_id,
            operation="write_off",
            quantity=quantity,
            user=user,
            reason=reason,
            document_number=document_number,
        )

    def adjust(self, variant_id: int, new_quantity: int, user: User, reason: str, comment: str | None = None):
        return self.record_movement(
            variant_id=variant_id,
            operation="adjustment",
            quantity=new_quantity,
            user=user,
            reason=reason,
            comment=comment,
        )

    def transfer(self, variant_id: int, quantity: int, from_warehouse_id: int, to_warehouse_id: int, user: User, reason: str | None = None):
        from_variant = self.variant_repo.get_by_id(variant_id)
        if not from_variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        if from_variant.quantity < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")

        from_variant.quantity -= quantity
        self.db.commit()
        self.stock_repo.create(
            variant_id=variant_id,
            warehouse_id=from_warehouse_id,
            user_id=user.id,
            operation="transfer",
            quantity=-quantity,
            reason=reason,
            reference_type="transfer_out",
            performed_by_name=user.email if user else None,
        )

        self.stock_repo.create(
            variant_id=variant_id,
            warehouse_id=to_warehouse_id,
            user_id=user.id,
            operation="transfer",
            quantity=quantity,
            reason=reason,
            reference_type="transfer_in",
            performed_by_name=user.email if user else None,
        )
        return True

    def get_movements(self, variant_id: int | None = None, operation: str | None = None, skip: int = 0, limit: int = 50):
        if variant_id:
            return self.stock_repo.list_by_variant(variant_id, skip, limit)
        return self.stock_repo.list_all(skip, limit)

    def get_movement_by_id(self, movement_id: int):
        return self.stock_repo.get_by_id(movement_id)
