"""Seed the database with initial data for development."""

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.warehouse import Warehouse
from app.models.customer import Customer
from app.models.promotion import Promotion
from app.models.loyalty import LoyaltyLevel
from app.models.supplier import Supplier
from app.models.color import Color
from app.models.size import Size
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.stock_movement import StockMovement
from app.models.setting import Setting
from app.models.company import Company
from datetime import datetime, timezone, timedelta
import random


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Database already seeded, skipping.")
        db.close()
        return

    admin_user = User(email="admin@shop.com", password_hash=hash_password("admin123"), role="super_admin")
    manager_user = User(email="manager@shop.com", password_hash=hash_password("manager123"), role="manager")
    cashier_user = User(email="cashier@shop.com", password_hash=hash_password("cashier123"), role="cashier")
    warehouse_user = User(email="warehouse@shop.com", password_hash=hash_password("warehouse123"), role="warehouse_employee")
    db.add_all([admin_user, manager_user, cashier_user, warehouse_user])
    db.flush()

    cats = ["T-Shirts", "Shirts", "Pants", "Jackets", "Suits", "Accessories"]
    cat_objs = []
    for cat in cats:
        c = Category(name=cat, slug=cat.lower().replace(" ", "-"))
        db.add(c)
        cat_objs.append(c)

    brands_data = ["Nike", "Adidas", "Zara", "H&M", "Levi's"]
    brand_objs = []
    for b in brands_data:
        brand = Brand(name=b, slug=b.lower().replace(" ", "-").replace("'", ""))
        db.add(brand)
        brand_objs.append(brand)

    db.flush()

    colors_data = [("Black", "#000000"), ("White", "#FFFFFF"), ("Navy", "#000080"), ("Gray", "#808080"), ("Red", "#FF0000"), ("Blue", "#0000FF")]
    color_objs = []
    for name, hex_val in colors_data:
        c = Color(name=name, hex_value=hex_val)
        db.add(c)
        color_objs.append(c)

    size_names = ["XS", "S", "M", "L", "XL", "XXL"]
    size_objs = []
    for i, name in enumerate(size_names):
        s = Size(name=name, sort_order=i)
        db.add(s)
        size_objs.append(s)

    db.flush()

    products_data = [
        ("Oversize T-Shirt", "oversize-t-shirt", "Classic oversized fit cotton t-shirt"),
        ("Slim Fit Shirt", "slim-fit-shirt", "Modern slim fit dress shirt"),
        ("Cargo Pants", "cargo-pants", "Casual cargo pants with multiple pockets"),
        ("Denim Jacket", "denim-jacket", "Classic denim jacket"),
        ("Wool Suit", "wool-suit", "Premium wool blend suit"),
        ("Leather Belt", "leather-belt", "Genuine leather belt"),
    ]
    sizes = ["S", "M", "L", "XL"]
    colors = ["Black", "White", "Navy"]
    all_variants = []

    for i, (name, slug, desc) in enumerate(products_data):
        product = Product(name=name, slug=slug, description=desc,
                          brand_id=brand_objs[i % len(brand_objs)].id,
                          category_id=cat_objs[i % len(cat_objs)].id, is_active=True)
        db.add(product)
        db.flush()

        for j, size_name in enumerate(sizes):
            for k, color_name in enumerate(colors):
                if (j + k) % 2 == 0:
                    continue
                color_obj = db.query(Color).filter(Color.name == color_name).first()
                size_obj = db.query(Size).filter(Size.name == size_name).first()
                barcode = f"200{i:02d}{j:02d}{k:02d}{random.randint(10,99)}"
                sku = f"SKU-{i:02d}{j:02d}{k:02d}"
                variant = ProductVariant(
                    product_id=product.id,
                    barcode=barcode,
                    sku=sku,
                    color_id=color_obj.id if color_obj else None,
                    size_id=size_obj.id if size_obj else None,
                    size=size_name,
                    color=color_name,
                    purchase_price=round(8.0 + i * 5 + j * 2 + random.uniform(0, 3), 2),
                    selling_price=round(20.0 + i * 10 + j * 5 + random.uniform(0, 5), 2),
                    quantity=random.randint(5, 100),
                )
                db.add(variant)
                all_variants.append(variant)

    db.flush()

    db.add(Warehouse(name="Main Warehouse", address="123 Commerce St"))
    db.add(Warehouse(name="Store Backroom", address="456 Retail Ave"))

    db.add(LoyaltyLevel(name="Bronze", min_spent=0, discount_percent=0))
    db.add(LoyaltyLevel(name="Silver", min_spent=500, discount_percent=5))
    db.add(LoyaltyLevel(name="Gold", min_spent=2000, discount_percent=10))
    db.add(LoyaltyLevel(name="Platinum", min_spent=5000, discount_percent=15))

    now = datetime.now(timezone.utc)
    db.add(Promotion(code="WELCOME10", discount_type="percent", discount_value=10,
                     min_amount=50, usage_limit=100, starts_at=now - timedelta(days=30),
                     ends_at=now + timedelta(days=365), is_active=True))
    db.add(Promotion(code="FLAT20", discount_type="fixed", discount_value=20,
                     min_amount=100, usage_limit=50, starts_at=now - timedelta(days=30),
                     ends_at=now + timedelta(days=30), is_active=True))

    db.add(Supplier(company_name="Textile Wholesale Inc.", contact_person="Bob Wilson",
                    phone="+111111111", email="sales@textilewholesale.com",
                    address="100 Factory Road", tax_number="TAX-001"))
    db.add(Supplier(company_name="Fashion Distribution Co.", contact_person="Alice Brown",
                    phone="+122222222", email="orders@fashiondist.com",
                    address="200 Apparel Ave", tax_number="TAX-002"))
    db.add(Supplier(company_name="Premium Garments Ltd.", contact_person="Charlie Davis",
                    phone="+133333333", email="info@premiumgarments.com",
                    address="300 Style Blvd", tax_number="TAX-003"))

    customers = [
        Customer(first_name="John", last_name="Doe", phone="+1234567890", loyalty_level="Bronze"),
        Customer(first_name="Jane", last_name="Smith", phone="+1234567891", loyalty_level="Silver", total_spent=1500),
        Customer(first_name="Mike", last_name="Johnson", phone="+1234567892", loyalty_level="Gold", total_spent=3500),
    ]
    for c in customers:
        db.add(c)
    db.flush()

    # Seed audit logs
    for action, entity in [("login", "user"), ("create", "product"), ("update", "variant"),
                           ("inventory_change", "variant"), ("create", "order")]:
        db.add(AuditLog(user_id=admin_user.id, user_email=admin_user.email,
                         action=action, entity=entity, entity_id=random.randint(1, 10)))

    # Seed stock movements
    if all_variants:
        for v in all_variants[:5]:
            db.add(StockMovement(variant_id=v.id, user_id=warehouse_user.id,
                                 operation="receiving", quantity=random.randint(20, 100),
                                 reason="Initial stock", performed_by_name=warehouse_user.email))

    # Seed notifications
    db.add(Notification(channel="sms", title="Order Confirmed", message="Order #1 confirmed. Thank you!",
                         status="sent", recipient="+1234567890", sent_at=now))
    db.add(Notification(channel="email", title="Welcome", message="Welcome to our store!",
                         status="sent", recipient="customer@example.com", sent_at=now))
    db.add(Notification(channel="sms", title="Failed Delivery", message="SMS delivery failed",
                         status="failed", recipient="+0000000000"))

    # Seed settings
    db.add(Setting(key="store_name", value="Clothes Shop"))
    db.add(Setting(key="currency", value="USD"))
    db.add(Setting(key="timezone", value="America/New_York"))
    db.add(Setting(key="receipt_footer", value="Thank you for your purchase!"))

    # Seed company profile
    db.add(Company(name="Clothes Shop Inc.", address="123 Commerce St, New York, NY 10001",
                   phone="+1 (555) 000-0000", email="info@clothesshop.com",
                   logo="", tin="TAX-00-1234567"))

    db.commit()
    db.close()
    print("Database seeded successfully!")
    print(f"  - {len(cats)} categories, {len(brands_data)} brands")
    print(f"  - {len(products_data)} products, {len(all_variants)} variants")
    print(f"  - {len(colors_data)} colors, {len(size_names)} sizes")
    print(f"  - {len(customers)} customers, 3 suppliers")
    print(f"  - Settings, Company, Audit logs, Notifications, Stock movements")


if __name__ == "__main__":
    seed()
