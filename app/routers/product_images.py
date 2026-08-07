import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.product_image import ProductImageCreate, ProductImageResponse, ProductImageUpdate as ProductImageUpdateSchema
from app.repositories.product_image_repo import ProductImageRepository
from app.utils.uploads import save_uploaded_image, UPLOAD_DIR

router = APIRouter(prefix="/api/products/{product_id}/images", tags=["product_images"])


@router.get("/", response_model=list[ProductImageResponse])
def list_images(product_id: int, db: Session = Depends(get_db)):
    return ProductImageRepository(db).list_by_product(product_id)


@router.post("/", response_model=ProductImageResponse)
def add_image(
    product_id: int,
    body: ProductImageCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    return ProductImageRepository(db).create(product_id, body.image_url, body.sort_order, body.is_main, body.color_id)


@router.post("/upload", response_model=ProductImageResponse)
def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    sort_order: int = Form(0),
    is_main: bool = Form(False),
    color_id: int | None = Form(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    filename = save_uploaded_image(file)
    image_url = filename
    return ProductImageRepository(db).create(product_id, image_url, sort_order, is_main, color_id)


@router.get("/file/{filename}")
def serve_image(filename: str):
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(str(filepath))


@router.patch("/{image_id}", response_model=ProductImageResponse)
def update_image(
    product_id: int,
    image_id: int,
    body: ProductImageUpdateSchema,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    repo = ProductImageRepository(db)
    if body.is_main:
        repo.clear_main(product_id)
    img = repo.update(image_id, **body.model_dump(exclude_none=True))
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return img


@router.delete("/{image_id}")
def delete_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    ProductImageRepository(db).delete(image_id)
    return {"ok": True}
