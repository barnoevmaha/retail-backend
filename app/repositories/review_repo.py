from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == id).first()

    def list_by_product(self, product_id: int, approved_only: bool = True) -> list[Review]:
        query = self.db.query(Review).filter(Review.product_id == product_id)
        if approved_only:
            query = query.filter(Review.is_approved == True)
        return query.order_by(Review.created_at.desc()).all()

    def list_all(self, skip: int = 0, limit: int = 50) -> list[Review]:
        return self.db.query(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Review:
        r = Review(**kwargs)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def update(self, review: Review, **kwargs) -> Review:
        for key, value in kwargs.items():
            setattr(review, key, value)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review: Review):
        self.db.delete(review)
        self.db.commit()
