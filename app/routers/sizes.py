from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.size_repo import SizeRepository
from app.schemas.size import SizeCreate, SizeResponse

router = APIRouter(prefix="/api/sizes", tags=["sizes"])


@router.get("/", response_model=list[SizeResponse])
def list_sizes(db: Session = Depends(get_db)):
    return SizeRepository(db).list_all()


@router.post("/", response_model=SizeResponse)
def create_size(
    body: SizeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    return SizeRepository(db).create(body.name, body.sort_order)
