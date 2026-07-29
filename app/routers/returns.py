from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.returns import ReturnCreate, ReturnItemCreate, ReturnConfirmResponse
from app.services.return_service import ReturnService

router = APIRouter(prefix="/api/returns", tags=["returns"])


class AddItemRequest(BaseModel):
    variant_id: int
    quantity: int = 1
    price: float = 0


@router.post("/")
def create_return(
    body: ReturnCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return_ = ReturnService(db).create(body.order_id, body.reason, body.notes, user)
    return {"id": return_.id, "order_id": return_.order_id, "status": return_.status}


@router.post("/{return_id}/items")
def add_item(
    return_id: int,
    body: AddItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return ReturnService(db).add_item(return_id, body.variant_id, body.quantity, body.price)


@router.post("/{return_id}/confirm", response_model=ReturnConfirmResponse)
def confirm_return(
    return_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return ReturnService(db).confirm(return_id, user)


@router.post("/{return_id}/cancel")
def cancel_return(
    return_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    ReturnService(db).cancel(return_id)
    return {"ok": True}


@router.get("/")
def list_returns(
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return ReturnService(db).list_all(status, skip, limit)


@router.get("/{return_id}")
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return ReturnService(db).get_detail(return_id)
