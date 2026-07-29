from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.writeoff import WriteOffCreate, WriteOffItemCreate, WriteOffConfirmResponse
from app.services.writeoff_service import WriteOffService

router = APIRouter(prefix="/api/writeoffs", tags=["writeoffs"])


class AddItemRequest(BaseModel):
    variant_id: int
    quantity: int = 1


@router.post("/")
def create_writeoff(
    body: WriteOffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    w = WriteOffService(db).create(body.reason, body.notes, user)
    return {"id": w.id, "reason": w.reason, "status": w.status}


@router.post("/{writeoff_id}/items")
def add_item(
    writeoff_id: int,
    body: AddItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return WriteOffService(db).add_item(writeoff_id, body.variant_id, body.quantity)


@router.post("/{writeoff_id}/confirm", response_model=WriteOffConfirmResponse)
def confirm_writeoff(
    writeoff_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return WriteOffService(db).confirm(writeoff_id, user)


@router.get("/")
def list_writeoffs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return WriteOffService(db).list_all(skip, limit)


@router.get("/{writeoff_id}")
def get_writeoff(
    writeoff_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return WriteOffService(db).get_detail(writeoff_id)
