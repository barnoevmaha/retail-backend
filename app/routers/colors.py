from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.color_repo import ColorRepository
from app.schemas.color import ColorCreate, ColorResponse

router = APIRouter(prefix="/api/colors", tags=["colors"])


@router.get("/", response_model=list[ColorResponse])
def list_colors(db: Session = Depends(get_db)):
    return ColorRepository(db).list_all()


@router.post("/", response_model=ColorResponse)
def create_color(
    body: ColorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    return ColorRepository(db).create(body.name, body.hex_value)
