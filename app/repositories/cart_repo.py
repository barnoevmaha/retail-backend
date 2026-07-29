from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_customer(self, customer_id: int) -> Cart | None:
        return self.db.query(Cart).filter(Cart.customer_id == customer_id).first()

    def get_by_session(self, session_key: str) -> Cart | None:
        return self.db.query(Cart).filter(Cart.session_key == session_key).first()

    def create_cart(self, **kwargs) -> Cart:
        c = Cart(**kwargs)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c

    def get_item(self, cart_id: int, variant_id: int) -> CartItem | None:
        return self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id, CartItem.variant_id == variant_id
        ).first()

    def add_item(self, cart_id: int, variant_id: int, quantity: int = 1) -> CartItem:
        item = CartItem(cart_id=cart_id, variant_id=variant_id, quantity=quantity)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        self.db.commit()
        return item

    def remove_item(self, item: CartItem):
        self.db.delete(item)
        self.db.commit()

    def clear_cart(self, cart_id: int):
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        self.db.commit()
