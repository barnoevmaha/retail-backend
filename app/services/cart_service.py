from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.cart_repo import CartRepository
from app.repositories.variant_repo import VariantRepository
from app.models.cart import CartItem
from app.models.variant import ProductVariant
from app.models.product import Product


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.variant_repo = VariantRepository(db)

    def get_or_create_cart(self, customer_id: int | None = None, session_key: str | None = None):
        cart = None
        if customer_id:
            cart = self.cart_repo.get_by_customer(customer_id)
        if not cart and session_key:
            cart = self.cart_repo.get_by_session(session_key)
        if not cart:
            cart = self.cart_repo.create_cart(customer_id=customer_id, session_key=session_key)
        return cart

    def add_item(self, cart_id: int, variant_id: int, quantity: int = 1):
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant or not variant.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        existing = self.cart_repo.get_item(cart_id, variant_id)
        new_qty = existing.quantity + quantity if existing else quantity
        if new_qty > variant.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Only {variant.quantity} available in stock")
        if existing:
            self.cart_repo.update_item(existing, new_qty)
        else:
            self.cart_repo.add_item(cart_id, variant_id, quantity)
        return self._build_cart(cart_id)

    def update_item_quantity(self, cart_id: int, item_id: int, quantity: int):
        if quantity < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be at least 1")
        item = self.db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        variant = self.variant_repo.get_by_id(item.variant_id)
        if variant and quantity > variant.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Only {variant.quantity} available in stock")
        self.cart_repo.update_item(item, quantity)
        return self._build_cart(cart_id)

    def remove_item(self, cart_id: int, item_id: int):
        item = self.db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        self.cart_repo.remove_item(item)
        return self._build_cart(cart_id)

    def clear_cart(self, cart_id: int):
        self.cart_repo.clear_cart(cart_id)

    def _build_cart(self, cart_id: int):
        items = self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
        result_items = []
        total = 0
        for item in items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            price = float(variant.selling_price) if variant else 0
            name = ""
            image_url = ""
            product_slug = ""
            product_id = None
            if variant:
                product = self.db.query(Product).filter(Product.id == variant.product_id).first()
                name = product.name if product else ""
                image_url = product.images[0].image_url if product and product.images else ""
                product_slug = product.slug if product else ""
                product_id = product.id if product else None
            result_items.append({
                "id": item.id,
                "variant_id": item.variant_id,
                "product_id": product_id,
                "product_slug": product_slug,
                "quantity": item.quantity,
                "price": price,
                "product_name": name,
                "name": name,
                "image_url": image_url,
                "size": variant.size if variant else None,
                "color": variant.color if variant else None,
                "color_hex": variant.color_rel.hex_value if variant and variant.color_rel else None,
                "stock": variant.quantity if variant else 0,
                "barcode": variant.barcode if variant else "",
            })
            total += price * item.quantity
        return {"id": cart_id, "items": result_items, "total": round(total, 2)}
