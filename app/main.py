from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import engine, Base
from app.core.config import settings
from app.routers import auth, users, products, variants, categories, brands, warehouse, customers, cart, checkout, orders, reviews, favorites, promotions, sms, analytics, suppliers, receiving, returns, writeoffs, adjustments, product_images, colors, sizes, audit_logs, notifications, pos_sessions, inventory_history, barcode_generator, receipts, settings as settings_router, company, export as export_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    yield
    engine.dispose()


app = FastAPI(title=settings.company_name + " API", lifespan=lifespan)

import os
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(variants.router)
app.include_router(categories.router)
app.include_router(brands.router)
app.include_router(warehouse.router)
app.include_router(customers.router)
app.include_router(cart.router)
app.include_router(checkout.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(favorites.router)
app.include_router(promotions.router)
app.include_router(sms.router)
app.include_router(analytics.router)
app.include_router(suppliers.router)
app.include_router(receiving.router)
app.include_router(returns.router)
app.include_router(writeoffs.router)
app.include_router(adjustments.router)
app.include_router(product_images.router)
app.include_router(colors.router)
app.include_router(sizes.router)
app.include_router(audit_logs.router)
app.include_router(settings_router.router)
app.include_router(company.router)
app.include_router(notifications.router)
app.include_router(pos_sessions.router)
app.include_router(inventory_history.router)
app.include_router(barcode_generator.router)
app.include_router(receipts.router)
app.include_router(export_data.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
