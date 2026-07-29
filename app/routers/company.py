from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.company_repo import CompanyRepository
from app.schemas.company import CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("", response_model=CompanyResponse | dict)
def get_company(db: Session = Depends(get_db)):
    company = CompanyRepository(db).get()
    if not company:
        return {"name": "Clothes Shop"}
    return company


@router.put("", response_model=CompanyResponse)
def update_company(
    body: CompanyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return CompanyRepository(db).upsert(**body.model_dump(exclude_unset=True))
