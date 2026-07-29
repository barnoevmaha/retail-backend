from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.adjustment import AdjustmentCreate, AdjustmentItemCreate, AdjustmentConfirmResponse
from app.services.adjustment_service import AdjustmentService

router = APIRouter(prefix="/api/adjustments", tags=["adjustments"])


class AddItemRequest(BaseModel):
    variant_id: int
    expected_quantity: int = 0
    actual_quantity: int = 0


@router.post("/")
def create_adjustment(
    body: AdjustmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    a = AdjustmentService(db).create(body.reason, body.notes, user)
    return {"id": a.id, "reason": a.reason, "status": a.status}


@router.post("/{adjustment_id}/items")
def add_item(
    adjustment_id: int,
    body: AddItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return AdjustmentService(db).add_item(adjustment_id, body.variant_id, body.expected_quantity, body.actual_quantity)


@router.post("/{adjustment_id}/confirm", response_model=AdjustmentConfirmResponse)
def confirm_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return AdjustmentService(db).confirm(adjustment_id, user)


@router.get("/")
def list_adjustments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return AdjustmentService(db).list_all(skip, limit)


@router.get("/{adjustment_id}")
def get_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return AdjustmentService(db).get_detail(adjustment_id)
