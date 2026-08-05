from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

# login as seed admin
r = c.post("/api/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
assert r.status_code == 200, r.text
tok = r.json()["access_token"]
H = {"Authorization": f"Bearer {tok}"}

# checkout an order
vs = c.get("/api/variants/?limit=5").json()["items"]
key = "confirm_test_" + __import__("secrets").token_hex(4)
c.post("/api/cart/items", json={"variant_id": vs[0]["id"], "quantity": 1}, headers={"X-Session-Key": key})
co = c.post("/api/checkout/", json={"payment_method": "cash", "session_key": key})
assert co.status_code == 200, co.text
oid = co.json()["id"]
print("checkout status:", co.json()["status"])

# PUT status confirmed
up = c.put(f"/api/orders/{oid}/status", json={"status": "confirmed"}, headers=H)
print("after update status:", up.status_code, up.json()["status"])

# list orders shape
lst = c.get("/api/orders/?limit=5", headers=H)
print("list keys:", list(lst.json().keys()), "items:", len(lst.json()["items"]))
print("first order:", {k: lst.json()["items"][0][k] for k in ("id", "status", "total_amount")})