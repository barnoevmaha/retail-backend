import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.repositories.user_repo import UserRepository
from app.models.user import User

client = TestClient(app)
db = SessionLocal()
repo = UserRepository(db)

TS = int(time.time())
EMAIL_STAFF = f"lockout-staff-{TS}@example.com"
EMAIL_STAFF2 = f"lockout-staff2-{TS}@example.com"
EMAIL_CUST = f"lockout-cust-{TS}@example.com"

staff1 = repo.create(EMAIL_STAFF, hash_password("CorrectPass!1"), "manager", "Lockout S1")
staff2 = repo.create(EMAIL_STAFF2, hash_password("CorrectPass!2"), "manager", "Lockout S2")
from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
cust = CustomerRepository(db).create(email=EMAIL_CUST, first_name="Lock", last_name="Cust",
                                     password_hash=hash_password("CustPass!1"))

ok = True

def login(email, pw):
    r = client.post("/api/auth/login", json={"email": email, "password": pw})
    return r

def show(label, results):
    print(f"{label}: " + ", ".join(f"{k}={v}" for k, v in results))

# ---- 1. 4 wrong passwords -> still 401, not locked
codes = []
r = login(EMAIL_STAFF, "wrong1")
codes.append(("m1", r.status_code))
r = login(EMAIL_STAFF, "wrong2")
codes.append(("m2", r.status_code))
r = login(EMAIL_STAFF, "wrong3")
codes.append(("m3", r.status_code))
r = login(EMAIL_STAFF, "wrong4")
codes.append(("m4", r.status_code))
show("1. staff 4x wrong", codes)
ok &= all(c == 401 for _, c in codes)

# ---- 2. 5th failed attempt -> 429 lockout
r = login(EMAIL_STAFF, "wrong5")
print("2. 5th wrong:", r.status_code, r.json().get("detail"))
ok &= r.status_code == 429

# ---- 3. further attempts during window -> 429
r = login(EMAIL_STAFF, "wrong6")
print("3. extra attempt:", r.status_code)
ok &= r.status_code == 429

# ---- 4. successful login resets counter (staff2: 4 wrong then correct)
codes = [login(EMAIL_STAFF2, f"WrongShit{x}").status_code for x in range(4)]
r = login(EMAIL_STAFF2, "CorrectPass!2")
print("4. staff2 4x wrong then correct:", codes, "-> correct:", r.status_code)
ok &= all(c == 401 for c in codes) and r.status_code == 200
# now staff2 should be unlocked and able to fail again without locking too fast
r = login(EMAIL_STAFF2, "wrong_after")
print("   staff2 wrong after reset:", r.status_code)
ok &= r.status_code == 401

# ---- 5. customer login uses its own protection (staff lockout must not affect it)
c1 = client.post("/api/customer/auth/login", json={"login": EMAIL_CUST, "password": "wrong!a"}).status_code
c2 = client.post("/api/customer/auth/login", json={"login": EMAIL_CUST, "password": "wrong!b"}).status_code
print("5. customer 2x wrong (its own counter):", c1, c2, "(staff lockout must NOT bleed here)")
ok &= c1 == 401 and c2 == 401

# ---- 6. staff login works normally for a fresh valid account
r = login(EMAIL_STAFF, "CorrectPass!1") if False else None
n = login(EMAIL_STAFF2, "CorrectPass!2")
print("6. valid login:", n.status_code)
ok &= n.status_code == 200

# ---- 7. different staff accounts don't block each other
r = login(EMAIL_STAFF, "wrong7")
r2 = login(EMAIL_STAFF2, "wrong7b")
print("7. locked staff1 still locked, staff2 independent:", r.status_code, r2.status_code)
ok &= r.status_code == 429 and r2.status_code == 401

# cleanup
db.query(Customer).filter(Customer.id == cust.id).delete()
repo_clean = db
db.query(User).filter(User.id == staff1.id).delete()
db.query(User).filter(User.id == staff2.id).delete()
db.commit()

print("PASS" if ok else "FAIL")