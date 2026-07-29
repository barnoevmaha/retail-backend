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

    def create_from_cart(self, cart_id: int, customer_id: int | None, payment_method: str | None, user: User | None = None):
        from app.models.cart import CartItem
        from app.models.product import Product

        items = self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        total = 0
        for item in items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            if not variant:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variant {item.variant_id} not found")
            if variant.quantity < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for variant {variant.id}")
            total += float(variant.selling_price) * item.quantity

        order = self.order_repo.create(
            customer_id=customer_id,
            user_id=user.id if user else None,
            total_amount=round(total, 2),
            payment_method=payment_method,
            status="pending",
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
                       new_values={"total": round(total, 2), "payment_method": payment_method, "items": len(items)})

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
