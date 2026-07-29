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
| SUPER_ADMIN_EMAIL | admin@example.com | Super admin email (dev placeholder) |
| SUPER_ADMIN_PASSWORD | ChangeMe123! | Super admin password (dev placeholder) |
| MANAGER_EMAIL | manager@example.com | Manager email (dev placeholder) |
| MANAGER_PASSWORD | ChangeMe123! | Manager password (dev placeholder) |
| CASHIER_EMAIL | cashier@example.com | Cashier email (dev placeholder) |
| CASHIER_PASSWORD | ChangeMe123! | Cashier password (dev placeholder) |
| WAREHOUSE_EMAIL | warehouse@example.com | Warehouse email (dev placeholder) |
| WAREHOUSE_PASSWORD | ChangeMe123! | Warehouse password (dev placeholder) |

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
4. Set required env vars: `SECRET_KEY`, and the seed credential vars below
5. Run one-off command: `python -m app.seed`
6. Done

### Production Credentials ⚠️

The seed creates default users from environment variables. **Never hardcode credentials in the repository.**

Set these on Railway (never in `.env.example` or committed files):

| Variable | Purpose |
|----------|---------|
| `SUPER_ADMIN_EMAIL` | Super admin login email |
| `SUPER_ADMIN_PASSWORD` | Super admin password |
| `MANAGER_EMAIL` | Manager login email |
| `MANAGER_PASSWORD` | Manager password |
| `CASHIER_EMAIL` | Cashier login email |
| `CASHIER_PASSWORD` | Cashier password |
| `WAREHOUSE_EMAIL` | Warehouse employee login email |
| `WAREHOUSE_PASSWORD` | Warehouse employee password |

If any variable is unset, the seed uses safe development placeholders (`admin@example.com` / `ChangeMe123!`). These are clearly marked as dev-only defaults and must be overridden in production.

## Health Check

GET /api/health → {"status": "ok"}
