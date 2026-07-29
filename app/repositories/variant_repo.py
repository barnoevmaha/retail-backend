from sqlalchemy.orm import Session

from app.models.variant import ProductVariant


class VariantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> ProductVariant | None:
        return self.db.query(ProductVariant).filter(ProductVariant.id == id).first()

    def get_by_barcode(self, barcode: str) -> ProductVariant | None:
        return self.db.query(ProductVariant).filter(ProductVariant.barcode == barcode).first()

    def get_by_sku(self, sku: str) -> ProductVariant | None:
        return self.db.query(ProductVariant).filter(ProductVariant.sku == sku).first()

    def list_by_product(self, product_id: int) -> list[ProductVariant]:
        return self.db.query(ProductVariant).filter(ProductVariant.product_id == product_id).all()

    def search(self, q: str = "", skip: int = 0, limit: int = 20) -> list[ProductVariant]:
        query = self.db.query(ProductVariant).filter(ProductVariant.is_active == True)
        if q:
            query = query.filter(
                ProductVariant.barcode.ilike(f"%{q}%")
                | ProductVariant.sku.ilike(f"%{q}%")
            )
        return query.offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ProductVariant:
        variant = ProductVariant(**kwargs)
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        return variant

    def update(self, variant: ProductVariant, **kwargs) -> ProductVariant:
        for key, value in kwargs.items():
            setattr(variant, key, value)
        self.db.commit()
        self.db.refresh(variant)
        return variant
