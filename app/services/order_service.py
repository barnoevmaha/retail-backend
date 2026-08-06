from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.order_repo import OrderRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.variant_repo import VariantRepository
from app.repositories.cart_repo import CartRepository
from app.models.user import User
from app.services.stock_service import StockService
from app.services.audit_service import AuditService
from app.services.receipt_service import ReceiptService


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.variant_repo = VariantRepository(db)
        self.cart_repo = CartRepository(db)
        self.stock_service = StockService(db)
        self.audit = AuditService(db)
        self.receipt_service = ReceiptService(db)

    def create_from_cart(self, cart_id: int, customer_id: int | None, payment_method: str | None, user: User | None = None, **delivery):
        from app.models.cart import CartItem
        from app.models.product import Product

        items = self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        subtotal = 0
        for item in items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            if not variant:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variant {item.variant_id} not found")
            if variant.quantity < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for variant {variant.id}")
            subtotal += float(variant.selling_price) * item.quantity

        # ponytail: flat fee, free above $500 — move to settings when pricing changes
        delivery_fee = 0.0 if subtotal >= 500 else 10.0
        total = round(subtotal + delivery_fee, 2)

        order = self.order_repo.create(
            customer_id=customer_id,
            user_id=user.id if user else None,
            total_amount=total,
            payment_method=payment_method,
            status="pending",
            customer_name=delivery.get("full_name"),
            customer_phone=delivery.get("phone"),
            city=delivery.get("city"),
            address=delivery.get("address"),
            apartment=delivery.get("apartment"),
            delivery_note=delivery.get("delivery_note"),
            delivery_fee=delivery_fee,
        )

        for item in items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            self.order_repo.add_item(order.id, item.variant_id, item.quantity, float(variant.selling_price))
            self.stock_service.sale(item.variant_id, item.quantity, user or User(), order.id)

        self.cart_repo.clear_cart(cart_id)

        if customer_id:
            customer = self.customer_repo.get_by_id(customer_id)
            if customer:
                self.customer_repo.update(customer, total_purchases=customer.total_purchases + 1,
                                          total_spent=float(customer.total_spent) + total)

        self.audit.log("create", "order", order.id, user,
                       new_values={"total": total, "payment_method": payment_method, "items": len(items)})

        try:
            self.receipt_service.create_from_order(order)
        except Exception:
            pass

        return order

    def get_order(self, order_id: int):
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    def build_response(self, order: "Order"):
        from app.models.product import Product
        from app.models.customer import Customer
        items = []
        subtotal = 0.0
        for it in order.items:
            variant = it.variant
            product = self.db.query(Product).filter(Product.id == variant.product_id).first() if variant else None
            subtotal += float(it.price) * it.quantity
            items.append({
                "id": it.id,
                "variant_id": it.variant_id,
                "quantity": it.quantity,
                "price": float(it.price),
                "product_name": product.name if product else "",
                "product_slug": product.slug if product else "",
                "image_url": product.images[0].image_url if product and product.images else "",
                "size": variant.size if variant else None,
                "color": variant.color if variant else None,
                "color_hex": variant.color_rel.hex_value if variant and variant.color_rel else None,
                "barcode": variant.barcode if variant else "",
            })
        customer = self.db.query(Customer).filter(Customer.id == order.customer_id).first() if order.customer_id else None
        customer_name = order.customer_name or (f"{customer.first_name} {customer.last_name}".strip() if customer else None)
        addr = order.address or ""
        if order.apartment:
            addr += f", apt. {order.apartment}"
        delivery = [l for l in [
            customer_name,
            order.city,
            addr or None,
            order.customer_phone,
        ] if l]
        delivery_fee = float(order.delivery_fee or 0)
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "notes": order.notes,
            "customer_name": customer_name,
            "customer_phone": order.customer_phone or (customer.phone if customer else None),
            "customer_email": customer.email if customer else None,
            "city": order.city,
            "address": order.address,
            "apartment": order.apartment,
            "delivery_note": order.delivery_note,
            "delivery_fee": delivery_fee,
            "subtotal": round(subtotal, 2),
            "shipping": delivery_fee,
            "items_count": len(items),
            "delivery": delivery,
            "items": items,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "customer": {
                "first_name": customer.first_name if customer else "",
                "last_name": customer.last_name if customer else "",
                "email": customer.email if customer else "",
                "phone": order.customer_phone or (customer.phone if customer else ""),
                "address": ", ".join([f for f in (order.city, order.address, order.apartment and f"apt. {order.apartment}") if f]),
            } if customer else None,
        }

    def update_status(self, order_id: int, status: str, user: User | None = None):
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        old_status = order.status
        updated = self.order_repo.update_status(order, status)
        self.audit.log("update", "order", order_id, user,
                       old_values={"status": old_status}, new_values={"status": status})
        return updated

    def list_orders(self, customer_id: int | None = None, status: str | None = None, skip: int = 0, limit: int = 50):
        if customer_id:
            return self.order_repo.list_by_customer(customer_id, skip, limit)
        return self.order_repo.list_all(status, skip, limit)
