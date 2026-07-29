from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.stock_movement import StockMovement
from app.models.variant import ProductVariant
from app.models.product import Product
from app.models.warehouse import Warehouse

router = APIRouter(prefix="/api/inventory-history", tags=["inventory-history"])


@router.get("")
def list_inventory_history(
    variant_id: int | None = Query(None),
    operation: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    query = db.query(StockMovement)
    if variant_id:
        query = query.filter(StockMovement.variant_id == variant_id)
    if operation:
        query = query.filter(StockMovement.operation == operation)
    movements = query.order_by(desc(StockMovement.created_at)).offset(skip).limit(limit).all()

    result = []
    for m in movements:
        variant = m.variant
        product_name = variant.product.name if variant and variant.product else ""
        warehouse_name = m.warehouse.name if m.warehouse else ""
        result.append({
            "id": m.id,
            "variant_id": m.variant_id,
            "product_name": product_name,
            "variant_sku": variant.sku if variant else "",
            "variant_barcode": variant.barcode if variant else "",
            "warehouse_id": m.warehouse_id,
            "warehouse_name": warehouse_name,
            "user_id": m.user_id,
            "operation": m.operation,
            "quantity": m.quantity,
            "reference_type": m.reference_type,
            "reference_id": m.reference_id,
            "document_number": m.document_number,
            "reason": m.reason,
            "comment": m.comment,
            "performed_by_name": m.performed_by_name,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return result
