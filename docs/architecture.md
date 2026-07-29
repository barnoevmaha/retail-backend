# Architecture

## Folder Structure

```
clothes-shop/
├── backend/                    # FastAPI + SQLAlchemy + PostgreSQL
│   └── app/
│       ├── core/               # Config, database, security, dependencies
│       ├── models/             # SQLAlchemy ORM models (21+ tables)
│       ├── schemas/            # Pydantic request/response schemas
│       ├── repositories/       # Data access layer (SQL queries)
│       ├── services/           # Business logic layer
│       ├── routers/            # API endpoints (FastAPI routers)
│       ├── utils/              # Helpers (barcode generator, etc.)
│       ├── main.py             # FastAPI app entry
│       └── seed.py             # Development seed data
├── admin/                      # React + Vite admin panel (Seller/Staff)
│   └── src/
│       ├── pages/              # Page components (~20)
│       ├── components/         # Shared components (Layout)
│       ├── context/            # AuthContext
│       └── api/                # Axios client
├── frontend/                   # React + Vite customer storefront
│   └── src/
│       ├── pages/              # Home, Catalog, Product, Cart
│       └── components/         # Navbar, ProductCard, etc.
├── telegram_bot/               # aiogram 3 Telegram bot
├── docker-compose.yml          # All services
└── docs/                       # Documentation
```

## Layered Architecture (Backend)

```
Router (HTTP) → Service (Business Logic) → Repository (Data Access) → Model (ORM)
```

- **Routers**: Handle HTTP, validation, RBAC. No business logic.
- **Services**: Business logic, transactions, audit logging. Call repositories.
- **Repositories**: SQLAlchemy queries. One class per entity.
- **Models**: SQLAlchemy ORM classes. Table definitions only.

## Database Schema (ER)

### Core Entities
- `users` - Staff accounts (super_admin, admin, manager, cashier, warehouse_employee)
- `customers` - Store customers (separate from users)
- `categories` - Product categories (hierarchical via parent_id)
- `brands` - Product brands
- `products` - Products with slug, description
- `product_variants` - SKU-level (barcode, color, size, prices, quantity)
- `product_images` - Image URLs per product

### Sales
- `carts` / `cart_items` - Shopping cart (session or customer)
- `orders` / `order_items` - Completed orders with line items
- `reviews` - Product reviews
- `favorites` - Customer wishlist

### Inventory
- `stock_movements` - ALL quantity changes (single source of truth)
- `warehouses` - Physical storage locations
- `suppliers` - Vendor companies
- `receiving` / `receiving_items` - Purchase receipts
- `returns` / `return_items` - Customer returns
- `writeoffs` / `writeoff_items` - Inventory write-offs
- `adjustments` / `adjustment_items` - Inventory corrections

### Enrichment
- `colors` - Normalized color catalog
- `sizes` - Normalized size catalog
- `promotions` - Discount codes
- `loyalty_levels` - Customer tiers
- `audit_logs` - All user actions (login, CRUD, inventory changes)
- `notifications` - Sent notifications (SMS, email, telegram, push)
- `sms_logs` - Legacy SMS log
- `pos_sessions` - Suspended POS sales

### Key Constraints
- **Barcode is UNIQUE** on `product_variants` - primary inventory identifier
- **All quantity changes** go through `stock_movements` — no direct `variant.quantity` edits
- **Color/Size** normalized with FK, legacy text columns for backward compat
- **Stock movements** record old/new values via AuditLog
