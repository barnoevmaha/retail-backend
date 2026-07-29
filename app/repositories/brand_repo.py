from sqlalchemy.orm import Session

from app.models.brand import Brand


class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Brand | None:
        return self.db.query(Brand).filter(Brand.id == id).first()

    def get_by_slug(self, slug: str) -> Brand | None:
        return self.db.query(Brand).filter(Brand.slug == slug).first()

    def list_all(self, active_only: bool = True) -> list[Brand]:
        query = self.db.query(Brand)
        if active_only:
            query = query.filter(Brand.is_active == True)
        return query.all()

    def create(self, **kwargs) -> Brand:
        brand = Brand(**kwargs)
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def update(self, brand: Brand, **kwargs) -> Brand:
        for key, value in kwargs.items():
            setattr(brand, key, value)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def delete(self, brand: Brand):
        self.db.delete(brand)
        self.db.commit()
