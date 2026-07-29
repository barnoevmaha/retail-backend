from sqlalchemy.orm import Session

from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_customer(self, customer_id: int) -> list[Favorite]:
        return self.db.query(Favorite).filter(Favorite.customer_id == customer_id).all()

    def get(self, customer_id: int, product_id: int) -> Favorite | None:
        return self.db.query(Favorite).filter(
            Favorite.customer_id == customer_id, Favorite.product_id == product_id
        ).first()

    def add(self, customer_id: int, product_id: int) -> Favorite:
        f = Favorite(customer_id=customer_id, product_id=product_id)
        self.db.add(f)
        self.db.commit()
        return f

    def remove(self, f: Favorite):
        self.db.delete(f)
        self.db.commit()
