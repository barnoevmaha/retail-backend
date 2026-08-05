from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.variant import ProductVariant
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


@router.delete("/{color_id}")
def delete_color(
    color_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    color = ColorRepository(db).get_by_id(color_id)
    if not color:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Color not found")
    db.query(ProductVariant).filter(ProductVariant.color_id == color_id).update({"color_id": None})
    db.delete(color)
    db.commit()
    return {"ok": True, "unlinked": True}
