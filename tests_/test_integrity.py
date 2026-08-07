import sys
import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.repositories.product_repo import ProductRepository
from app.repositories.variant_repo import VariantRepository
from app.repositories.brand_repo import BrandRepository
from app.repositories.category_repo import CategoryRepository
from app.repositories.color_repo import ColorRepository
from app.repositories.product_image_repo import ProductImageRepository
from app.models.product_image import ProductImage
from app.repositories.stock_repo import StockMovementRepository
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.pos_session import PosSession
from app.models.category import Category
from app.models.brand import Brand
from app.models.color import Color
from app.services.stock_service import StockService
from app.models.user import User
from decimal import Decimal

client = TestClient(app)
db = SessionLocal()
tok = create_access_token({"sub": "1", "role": "super_admin"})
H = {"Authorization": f"Bearer {tok}"}
TS = int(time.time())
ok = True

def fresh(prefix, cls, **kw):
    return cls(db).create(**kw) if False else None

# ============ 1. product delete: blocked when history exists ============
pr = ProductRepository(db).create(name=f"I9 P {TS}", slug=f"i9-p-{TS}")
v = VariantRepository(db).create(product_id=pr.id, barcode=f"i9b{TS}", sku=f"i9s{TS}",
                                 purchase_price=10, selling_price=20, quantity=5)
pr_id, v_id = pr.id, v.id
o = Order(status="pending", total_amount=Decimal("20.00"), payment_method="card")
db.add(o); db.commit(); db.refresh(o)
db.add(OrderItem(order_id=o.id, variant_id=v.id, quantity=1, price=Decimal("20.00"))); db.commit()

r = client.delete(f"/api/products/{pr.id}", headers=H)
print("1. delete product w/ order history:", r.status_code, r.json().get("detail"))
ok &= r.status_code == 409
db.query(OrderItem).filter(OrderItem.order_id == o.id).delete()
db.query(Order).filter(Order.id == o.id).delete()
db.commit()

# ============ 1b. product delete: blocked when stock history exists ============
StockMovementRepository(db).create(variant_id=v.id, user_id=1, operation="receiving", quantity=5)
db.commit()
r = client.delete(f"/api/products/{pr.id}", headers=H)
print("1b. delete product w/ stock history:", r.status_code)
ok &= r.status_code == 409
db.query(StockMovement).filter(StockMovement.variant_id == v.id).delete(); db.commit()

# ============ 1c. product delete: allowed with only cart items ============
cart = Cart(session_key=f"i9cart{TS}"); db.add(cart); db.commit(); db.refresh(cart)
db.add(CartItem(cart_id=cart.id, variant_id=v.id, quantity=1)); db.commit()
r = client.delete(f"/api/products/{pr.id}", headers=H)
print("1c. delete product w/ only cart:", r.status_code)
ok &= r.status_code == 200
left = db.query(Product).filter(Product.id == pr_id).first()
left_v = db.query(ProductVariant).filter(ProductVariant.id == v_id).first()
left_c = db.query(CartItem).filter(CartItem.cart_id == cart.id).first()
print("    product gone:", left is None, "| variant gone:", left_v is None, "| cart item cleaned:", left_c is None)
ok &= left is None and left_v is None and left_c is None

# ============ 2. category delete blocked when products exist ============
cat = CategoryRepository(db).create(name=f"I9 Cat {TS}", slug=f"i9-cat-{TS}")
cat_id = cat.id
pr2 = ProductRepository(db).create(name=f"I9 P2 {TS}", slug=f"i9-p2-{TS}", category_id=cat.id)
r = client.delete(f"/api/categories/{cat.id}", headers=H)
print("2. delete category w/ product:", r.status_code, r.json().get("detail"))
ok &= r.status_code == 409
db.query(Product).filter(Product.id == pr2.id).delete(); db.commit()

# ============ 3. brand delete blocked when products exist ============
brand = BrandRepository(db).create(name=f"I9 Brand {TS}", slug=f"i9-brand-{TS}")
brand_id = brand.id
pr3 = ProductRepository(db).create(name=f"I9 P3 {TS}", slug=f"i9-p3-{TS}", brand_id=brand.id)
r = client.delete(f"/api/brands/{brand.id}", headers=H)
print("3. delete brand w/ product:", r.status_code, r.json().get("detail"))
ok &= r.status_code == 409
db.query(Product).filter(Product.id == pr3.id).delete(); db.commit()

# ============ 4. color delete unlinks variants AND images ============
color = ColorRepository(db).create(name=f"I9C{TS}", hex_value="#123456")
color_id = color.id
pr4 = ProductRepository(db).create(name=f"I9 P4 {TS}", slug=f"i9-p4-{TS}")
v4 = VariantRepository(db).create(product_id=pr4.id, barcode=f"i9b4{TS}", sku=f"i9s4{TS}", color_id=color.id,
                                  purchase_price=1, selling_price=2)
img = ProductImageRepository(db).create(product_id=pr4.id, image_url="/uploads/x.jpg", color_id=color.id)
r = client.delete(f"/api/colors/{color.id}", headers=H)
db.refresh(v4); db.refresh(img)
print("4. delete color:", r.status_code, "| variant color:", v4.color_id, "| img color:", img.color_id)
ok &= r.status_code == 200 and v4.color_id is None and img.color_id is None
db.query(ProductImage).filter(ProductImage.id == img.id).delete()
db.query(ProductVariant).filter(ProductVariant.id == v4.id).delete()
db.query(Product).filter(Product.id == pr4.id).delete(); db.commit()

# ============ 5. stock movement persists w/o audit-repo commit dependency ============
pr5 = ProductRepository(db).create(name=f"I9 P5 {TS}", slug=f"i9-p5-{TS}")
v5 = VariantRepository(db).create(product_id=pr5.id, barcode=f"i9b5{TS}", sku=f"i9s5{TS}",
                                  purchase_price=10, selling_price=20, quantity=10)
user = db.query(User).filter(User.id == 1).first()
m = StockService(db).record_movement(v5.id, "receiving", 5, user, reason="I9 test")
db.expire_all()
v5b = db.query(ProductVariant).filter(ProductVariant.id == v5.id).first()
m2 = db.query(StockMovement).filter(StockMovement.id == m.id).first()
print("5. movement persisted:", m2 is not None, "| qty after:", v5b.quantity)
ok &= m2 is not None and v5b.quantity == 15

# ============ 6. POS session money total stays Numeric-precise ============
r = client.post("/api/pos-sessions/", headers=H,
                json={"items": "[]", "customer_name": "I9", "total": 1234.56, "payment_method": "card"})
sid = r.json()["id"]
s = db.query(PosSession).filter(PosSession.id == sid).first()
print("6. POS total stored:", s.total, type(s.total).__name__, "| api:", r.json()["total"])
ok &= r.status_code == 200 and s.total == Decimal("1234.56") and r.json()["total"] == 1234.56

# cleanup (FK-safe order, captured ids only)
for m_id in (m.id,):
    db.query(StockMovement).filter(StockMovement.variant_id.in_([v_id, v5.id, 0])).delete(synchronize_session=False)
db.query(StockMovement).filter(StockMovement.reason == "I9 test").delete(synchronize_session=False)
db.query(CartItem).filter(CartItem.cart_id == cart.id).delete(synchronize_session=False)
db.query(CartItem).filter(CartItem.variant_id.in_([v_id, v5.id, 0])).delete(synchronize_session=False)
db.query(Cart).filter(Cart.id == cart.id).delete(synchronize_session=False)
db.query(ProductVariant).filter(ProductVariant.id.in_([v_id, v5.id])).delete(synchronize_session=False)
db.query(Product).filter(Product.id.in_([pr_id, pr5.id, pr2.id, pr3.id, pr4.id])).delete(synchronize_session=False)
db.query(Category).filter(Category.id == cat_id).delete(synchronize_session=False)
db.query(Brand).filter(Brand.id == brand_id).delete(synchronize_session=False)
db.query(Color).filter(Color.id == color_id).delete(synchronize_session=False)
db.query(PosSession).filter(PosSession.id == sid).delete(synchronize_session=False)
db.commit()

print("PASS" if ok else "FAIL")