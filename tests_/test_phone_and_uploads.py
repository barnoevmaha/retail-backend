import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
TS = int(time.time())

# 1. Phone must contain at least 4 digits (charset-only "0-0-0-" must be rejected).
cart_key = f"iphone{TS}"
client.post("/api/cart/items", json={"variant_id": 1, "quantity": 1}, headers={"X-Session-Key": cart_key})
r = client.post("/api/checkout/", headers={"X-Session-Key": cart_key}, json={
    "payment_method": "manual",
    "full_name": "Phone Test", "phone": "0-0-0-", "city": "Tashkent", "address": "Street 1",
})
print("1. phone '0-0-0-' rejected:", r.status_code, r.json().get("detail"))
assert r.status_code == 422 and "4 digits" in r.json()["detail"]

# 2. Valid phone passes (>=4 digits).
r2 = client.post("/api/checkout/", headers={"X-Session-Key": cart_key}, json={
    "payment_method": "manual",
    "full_name": "Phone Test", "phone": "+998 90 123 45 67", "city": "Tashkent", "address": "Street 1",
})
print("2. valid phone checkout:", r2.status_code, r2.json().get("payment_status"))
assert r2.status_code == 200 and r2.json()["payment_status"] == "pending"

# 3. serve_image extension whitelist + traversal guard.
t1 = client.get("/api/products/1/images/file/evil.svg")
print("3a. svg rejected:", t1.status_code)
assert t1.status_code in (400, 404)
t2 = client.get("/api/products/1/images/file/..%2F..%2F.env")
print("3b. traversal rejected:", t2.status_code)
assert t2.status_code in (400, 404, 405)
t3 = client.get("/api/products/1/images/file/..%2Fconfig.py")
print("3c. dotdot rejected:", t3.status_code)
assert t3.status_code in (400, 404, 405)
t4 = client.get("/api/products/1/images/file/evil.txt")
print("3d. txt rejected:", t4.status_code)
assert t4.status_code in (400, 404)
t5 = client.get("/api/products/1/images/file/47f7d5ea9d5445fbbf8ca753a816a283.jpg")
print("3e. valid jpg (unknown id):", t5.status_code)
assert t5.status_code in (200, 404)

print("PASS")
