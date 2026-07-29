# retail-backend

REST API for the Retail Management System. Built with FastAPI + SQLAlchemy + PostgreSQL.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- JWT authentication (python-jose + bcrypt)
- Alembic (migrations)
- OpenPyXL (XLSX export)

## Architecture

```
routers/ → services/ → repositories/ → models/
```

Business logic lives in services, never in routers. All quantity changes go through StockService.record_movement().

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://clothes_shop:clothes_shop@localhost:5432/clothes_shop | PostgreSQL connection string |
| SECRET_KEY | dev-secret-key-change-in-production | JWT signing key |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token expiry |
| REFRESH_TOKEN_EXPIRE_DAYS | 30 | Refresh token expiry |
| CORS_ORIGINS | * | Comma-separated allowed origins |
| FRONTEND_URL | | Frontend URL for CORS |
| ADMIN_URL | | Admin URL for CORS |
| UPLOAD_DIR | uploads | File upload directory |
| SMS_PROVIDER | mock | SMS provider (mock/...) |
| TELEGRAM_BOT_TOKEN | | Bot token for notifications |
| COMPANY_NAME | Clothes Shop | Display name |

## Development

```bash
cp .env.example .env
# Start PostgreSQL, then:
uvicorn app.main:app --reload --port 8000

# Seed demo data:
python -m app.seed
```

## API Routes

129 routes covering:
- Auth & Users
- Products, Variants, Categories, Brands
- Colors, Sizes, Product Images
- Cart & Checkout
- Orders & Customers
- Inventory & Warehouse
- Stock Movements (receiving, returns, write-offs, adjustments)
- Suppliers
- POS Sessions
- Promotions, Reviews, Favorites
- Analytics
- Export (CSV/XLSX)
- Receipts (HTML with QR)
- Settings & Company
- Audit Logs
- Notifications
- SMS Logs
- Barcode Generator

## Railway Deployment

1. Push this repo to GitHub
2. In Railway, create a new project from the repo
3. Add PostgreSQL plugin (Railway sets DATABASE_URL automatically)
4. Set required env vars: SECRET_KEY
5. Run one-off command: `python -m app.seed`
6. Done

## Health Check

GET /api/health → {"status": "ok"}
