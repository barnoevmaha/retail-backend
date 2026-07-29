from sqlalchemy.orm import Session

from app.repositories.receipt_repo import ReceiptRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.setting_repo import SettingRepository
from app.models.receipt import Receipt
from app.models.order import OrderItem
from app.models.variant import ProductVariant
from app.models.product import Product


class ReceiptService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReceiptRepository(db)

    def create_from_order(self, order):
        company = CompanyRepository(self.db).get()
        settings = SettingRepository(self.db).get_many()

        receipt_number = f"RCP-{order.id:05d}"

        receipt = self.repo.create(
            order_id=order.id,
            receipt_number=receipt_number,
            customer_id=order.customer_id,
            customer_name=f"{order.customer.first_name} {order.customer.last_name}" if order.customer else None,
            total_amount=float(order.total_amount),
            payment_method=order.payment_method,
            status="completed",
            store_name=company.name if company else settings.get("store_name", "Clothes Shop"),
            store_address=company.address if company else None,
            store_phone=company.phone if company else None,
            store_tin=company.tin if company else None,
        )

        order_items = (
            self.db.query(OrderItem)
            .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        for item in order_items:
            product_name = item.variant.product.name if item.variant and item.variant.product else None
            barcode = item.variant.barcode if item.variant else None
            self.repo.add_item(receipt.id, item.variant_id, product_name, barcode, item.quantity, float(item.price))

        self.db.commit()
        self.db.refresh(receipt)
        return receipt

    def get_history(self, skip: int = 0, limit: int = 50):
        return self.repo.list_all(skip, limit)

    def get_by_id(self, receipt_id: int):
        return self.repo.get_by_id(receipt_id)
