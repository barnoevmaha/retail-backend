from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.receiving import (
    ReceivingCreate,
    ReceivingStartResponse,
    ReceivingConfirmResponse,
    ReceivingItemCreate,
    ReceivingItemResponse,
)
from app.services.receiving_service import ReceivingService

router = APIRouter(prefix="/api/receiving", tags=["receiving"])


class AddByBarcodeRequest(BaseModel):
    barcode: str
    quantity: int = 1
    purchase_price: float = 0


class CreateVariantAndAddRequest(BaseModel):
    barcode: str
    sku: str
    product_id: int
    size: str | None = None
    color: str | None = None
    quantity: int = 1
    purchase_price: float = 0


@router.post("/start", response_model=ReceivingStartResponse)
def start_receiving(
    body: ReceivingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return ReceivingService(db).start(
        supplier_id=body.supplier_id,
        invoice_number=body.invoice_number,
        received_date=body.received_date,
        notes=body.notes,
        user=user,
    )


@router.post("/{receiving_id}/items", response_model=ReceivingItemResponse)
def add_item(
    receiving_id: int,
    body: ReceivingItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return ReceivingService(db).add_item(receiving_id, body.variant_id, body.quantity, body.purchase_price)


@router.post("/{receiving_id}/add-by-barcode", response_model=ReceivingItemResponse)
def add_by_barcode(
    receiving_id: int,
    body: AddByBarcodeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    service = ReceivingService(db)
    return service.add_item_by_barcode(receiving_id, body.barcode, body.quantity, body.purchase_price)


@router.post("/{receiving_id}/create-variant-and-add", response_model=ReceivingItemResponse)
def create_variant_and_add(
    receiving_id: int,
    body: CreateVariantAndAddRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    service = ReceivingService(db)
    return service.create_variant_and_add(
        receiving_id, body.barcode, body.sku, body.product_id,
        body.size, body.color, body.quantity, body.purchase_price,
    )


@router.post("/{receiving_id}/confirm", response_model=ReceivingConfirmResponse)
def confirm_receiving(
    receiving_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return ReceivingService(db).confirm(receiving_id, user)


@router.post("/{receiving_id}/cancel")
def cancel_receiving(
    receiving_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    ReceivingService(db).cancel(receiving_id)
    return {"ok": True}


@router.get("/")
def list_receivings(
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return ReceivingService(db).list_all(status, skip, limit)


@router.get("/{receiving_id}")
def get_receiving(
    receiving_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return ReceivingService(db).get_detail(receiving_id)
