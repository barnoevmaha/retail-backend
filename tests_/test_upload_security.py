import io
import os
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.repositories.brand_repo import BrandRepository
from app.repositories.product_repo import ProductRepository
from app.models.product_image import ProductImage
from app.models.brand import Brand
from app.models.product import Product

client = TestClient(app)
db = SessionLocal()
tok = create_access_token({"sub": "1", "role": "super_admin"})
H = {"Authorization": f"Bearer {tok}"}

ok = True

def upload(url, data, filename, content, ctype="application/octet-stream"):
    return client.post(url, headers=H, data=data,
                       files={"file": (filename, io.BytesIO(content), ctype)})

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 200
HTML = b"<html><script>alert(1)</script></html>"
SVG = b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>"
FAKE_JPG = b"\xff\xd8\xff" + b"<script>alert(1)</script>"

# fixtures
import time
_uq = int(time.time())
brand = BrandRepository(db).create(name=f"UploadTest{_uq}", slug=f"upload-test-b-{_uq}")
product = ProductRepository(db).create(name=f"UploadTest P{_uq}", slug=f"upload-test-p-{_uq}")

# ---- 1-3. valid JPEG / PNG / WebP accepted (product images)
for ext, content in [("jpg", JPEG), ("png", PNG), ("webp", WEBP)]:
    r = upload(f"/api/products/{product.id}/images/upload", {}, f"x.{ext}", content)
    print(f"1-3. valid {ext}: {r.status_code}")
    ok &= r.status_code == 200

# brand logo JPEG
r = upload(f"/api/brands/{brand.id}/logo", {}, "logo.jpg", JPEG)
print("10. brand logo JPEG:", r.status_code, r.json().get("logo"))
ok &= r.status_code == 200 and r.json()["logo"].startswith("/uploads/")

# ---- 4. fake .jpg containing HTML -> rejected (HTML has no JPEG magic)
r = upload(f"/api/products/{product.id}/images/upload", {}, "fake.jpg", HTML)
print("4. fake .jpg with HTML:", r.status_code)
ok &= r.status_code == 415

# ---- 5. .html -> rejected
r = upload(f"/api/products/{product.id}/images/upload", {}, "evil.html", HTML)
print("5. .html:", r.status_code)
ok &= r.status_code == 415

# ---- 6. .svg -> rejected
r = upload(f"/api/products/{product.id}/images/upload", {}, "evil.svg", SVG)
print("6. .svg:", r.status_code)
ok &= r.status_code == 415

# ---- 7. wrong MIME with valid content -> accepted (content decides)
r = upload(f"/api/products/{product.id}/images/upload", {}, "x.png", PNG, "text/html")
print("7. PNG bytes + text/html MIME:", r.status_code)
ok &= r.status_code == 200

# ---- 7b. correct MIME (image/jpeg) with SVG content -> rejected
r = upload(f"/api/products/{product.id}/images/upload", {}, "x.jpg", SVG, "image/jpeg")
print("7b. image/jpeg MIME + SVG content:", r.status_code)
ok &= r.status_code == 415

# ---- 8. oversized file -> 413
big = JPEG + b"A" * (6 * 1024 * 1024)
r = upload(f"/api/products/{product.id}/images/upload", {}, "big.jpg", big)
print("8. oversized (6MB):", r.status_code)
ok &= r.status_code == 413
leftover = [f for f in os.listdir("uploads") if Path("uploads", f).stat().st_size > 5 * 1024 * 1024]
print("   leftover oversized files:", leftover)
ok &= not leftover

# ---- 9. product image upload works end-to-end (URL serves via /uploads)
r = upload(f"/api/products/{product.id}/images/upload", {}, "p.jpg", JPEG)
img = r.json()["image_url"]
ok &= r.status_code == 200
srv = client.get(img)
print("9. served image:", srv.status_code, srv.headers.get("content-type"), "nosniff:", srv.headers.get("x-content-type-options"))
ok &= srv.status_code == 200 and srv.headers.get("x-content-type-options") == "nosniff"

# ---- 11. existing uploaded images still render (the one from test 9)
print("11. existing image still 200:", srv.status_code)
ok &= srv.status_code == 200

# cleanup
db.query(ProductImage).filter(ProductImage.product_id == product.id).delete()
db.query(Product).filter(Product.id == product.id).delete()
db.query(Brand).filter(Brand.id == brand.id).delete()
db.commit()

print("PASS" if ok else "FAIL")