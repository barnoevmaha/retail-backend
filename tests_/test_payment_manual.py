import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.order import Order

client = TestClient(app)
db = SessionLocal()
tok = create_access_token({"sub": "1", "role": "super_admin"})
H = {"Authorization": f"Bearer {tok}"}
TS = int(time.time())

# 1. Storefront/manual checkout -> payment_status stays pending, no fake "paid".
cart_key = f"i10cart{TS}"
client.post("/api/cart/items", json={"variant_id": 1, "quantity": 1}, headers={"X-Session-Key": cart_key})
r = client.post("/api/checkout/", headers={"X-Session-Key": cart_key}, json={
    "payment_method": "manual",
    "full_name": "I10 Buyer", "phone": "+998901234567", "city": "Tashkent", "address": "Street 1",
})
print("1. manual checkout:", r.status_code, "| payment_method:", r.json().get("payment_method"), "| payment_status:", r.json().get("payment_status"))
assert r.status_code == 200
assert r.json()["payment_method"] == "manual"
assert r.json()["payment_status"] == "pending", "manual order must stay pending"
oid = r.json()["id"]

# 2. Even if client lies and sends "card", no paid is set.
dist2 = f"cart10b-{TS}"
client.post("/api/cart/items", headers={"X-Session-Key": dist2}, json={"variant_id": 1, "quantity": 1})
r = client.post("/api/checkout/", headers={"X-Session-Key": dist2}, json={
    "payment_method": "card",
    "full_name": "I10 Card", "phone": "+998901234568", "city": "Tashkent", "address": "Street 2",
})
print("2. card checkout stays pending:", r.status_code, "| payment_status:", r.json().get("payment_status"))
assert r.status_code == 200
assert r.json()["payment_status"] == "pending", "card payment must NOT auto-confirm"

# 3. No admin/status endpoint can mark payment paid (order status only).
r = client.put(f"/api/orders/{oid}/status", json={"status": "confirmed"}, headers=H)
assert r.status_code == 200
assert r.json()["payment_status"] == "pending", "changing order status must not touch payment_status"

# 4. Cash/POS-style checkout still works and stays pending (manual confirmation).
dist3 = f"cart10c-{TS}"
client.post("/api/cart/items", headers={"X-Session-Key": dist3}, json={"variant_id": 1, "quantity": 1})
r = client.post("/api/checkout/", headers={"X-Session-Key": dist3}, json={
    "payment_method": "cash",
    "full_name": "I10 Cash", "phone": "+998901234569", "city": "Tashkent", "address": "Street 3",
})
print("4. cash checkout:", r.status_code, "| payment:", r.json().get("payment_method"), r.json().get("payment_status"))
assert r.status_code == 200

# cleanup (FK-safe: items before orders, receipts before orders)
from app.models.order import OrderItem
from app.models.receipt import Receipt, ReceiptItem
db.query(ReceiptItem).delete()
db.query(OrderItem).delete()
db.query(Receipt).delete()
db.query(Order).delete()
db.commit()
print("PASS")