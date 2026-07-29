from sqlalchemy.orm import Session

from app.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_product(self, product_id: int) -> list[ProductImage]:
        return self.db.query(ProductImage).filter(ProductImage.product_id == product_id).order_by(ProductImage.sort_order).all()

    def create(self, product_id: int, image_url: str, sort_order: int = 0, is_main: bool = False) -> ProductImage:
        img = ProductImage(product_id=product_id, image_url=image_url, sort_order=sort_order, is_main=is_main)
        self.db.add(img)
        self.db.commit()
        self.db.refresh(img)
        return img

    def update(self, image_id: int, **kwargs) -> ProductImage | None:
        img = self.db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not img:
            return None
        for k, v in kwargs.items():
            setattr(img, k, v)
        self.db.commit()
        self.db.refresh(img)
        return img

    def clear_main(self, product_id: int):
        self.db.query(ProductImage).filter(ProductImage.product_id == product_id, ProductImage.is_main == True).update({"is_main": False})

    def delete(self, image_id: int):
        self.db.query(ProductImage).filter(ProductImage.id == image_id).delete()
        self.db.commit()
