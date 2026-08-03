from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.models.variant import ProductVariant


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == id).first()

    def get_by_slug(self, slug: str) -> Product | None:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def search(self, q: str = "", category_id: int | None = None, brand_id: int | None = None,
               color_id: int | None = None, size_id: int | None = None,
               barcode: str = "", sku: str = "",
               is_active: bool | None = True,
               skip: int = 0, limit: int = 20) -> list[Product]:
        query = self.db.query(Product)
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        if q:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%"),
                )
            )
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if barcode:
            query = query.join(ProductVariant).filter(ProductVariant.barcode == barcode)
        if sku:
            query = query.join(ProductVariant).filter(ProductVariant.sku.ilike(f"%{sku}%"))
        if color_id:
            query = query.join(ProductVariant).filter(ProductVariant.color_id == color_id)
        if size_id:
            query = query.join(ProductVariant).filter(ProductVariant.size_id == size_id)

        return query.offset(skip).limit(limit).all()

    def count(self, q: str = "", category_id: int | None = None, brand_id: int | None = None,
              color_id: int | None = None, size_id: int | None = None,
              barcode: str = "", sku: str = "",
              is_active: bool | None = True) -> int:
        query = self.db.query(Product)
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        if q:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%"),
                )
            )
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if barcode:
            query = query.join(ProductVariant).filter(ProductVariant.barcode == barcode)
        if sku:
            query = query.join(ProductVariant).filter(ProductVariant.sku.ilike(f"%{sku}%"))
        if color_id:
            query = query.join(ProductVariant).filter(ProductVariant.color_id == color_id)
        if size_id:
            query = query.join(ProductVariant).filter(ProductVariant.size_id == size_id)
        return query.count()

    def create(self, **kwargs) -> Product:
        product = Product(**kwargs)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.commit()
