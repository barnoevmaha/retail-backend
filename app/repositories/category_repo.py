from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == id).first()

    def get_by_slug(self, slug: str) -> Category | None:
        return self.db.query(Category).filter(Category.slug == slug).first()

    def list_all(self, active_only: bool = True) -> list[Category]:
        query = self.db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.order_by(Category.sort_order).all()

    def create(self, **kwargs) -> Category:
        cat = Category(**kwargs)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def update(self, cat: Category, **kwargs) -> Category:
        for key, value in kwargs.items():
            setattr(cat, key, value)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def delete(self, cat: Category):
        self.db.delete(cat)
        self.db.commit()
