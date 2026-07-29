from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.supplier_repo import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/")
def list_suppliers(
    search: str = Query(""),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repo = SupplierRepository(db)
    suppliers = repo.list_all(search, skip, limit)
    total = repo.count(search)
    return {
        "items": [SupplierResponse.model_validate(s) for s in suppliers],
        "total": total,
    }


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    repo = SupplierRepository(db)
    supplier = repo.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    body: SupplierCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    return SupplierRepository(db).create(**body.model_dump())


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    body: SupplierUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = SupplierRepository(db)
    supplier = repo.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return repo.update(supplier, **body.model_dump(exclude_unset=True))
