from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.repositories.warehouse_repo import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.schemas.stock import StockMovementCreate, StockMovementResponse
from app.services.stock_service import StockService

router = APIRouter(prefix="/api/warehouse", tags=["warehouse"])


@router.get("/", response_model=list[WarehouseResponse])
def list_warehouses(db: Session = Depends(get_db)):
    return WarehouseRepository(db).list_all()


@router.post("/", response_model=WarehouseResponse)
def create_warehouse(
    body: WarehouseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return WarehouseRepository(db).create(**body.model_dump())


@router.post("/receive", response_model=StockMovementResponse)
def receive_stock(
    body: StockMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    service = StockService(db)
    return service.receive(body.variant_id, body.quantity, body.warehouse_id, user, body.reason)


@router.post("/write-off", response_model=StockMovementResponse)
def write_off(
    body: StockMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    service = StockService(db)
    return service.write_off(body.variant_id, body.quantity, user, body.reason or "write-off")


@router.post("/adjust", response_model=StockMovementResponse)
def adjust_stock(
    body: StockMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager")),
):
    service = StockService(db)
    return service.adjust(body.variant_id, body.quantity, user, body.reason or "adjustment")


@router.get("/movements", response_model=list[StockMovementResponse])
def list_movements(
    variant_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return StockService(db).get_movements(variant_id, skip, limit)
