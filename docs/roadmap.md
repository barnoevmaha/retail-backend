# Development Roadmap

## Phase 1 — Foundation ✓
- Docker, config, database, auth, RBAC, User model

## Phase 2 — Catalog ✓
- Product, Category, Brand, ProductVariant, ProductImage
- StockMovement with operations

## Phase 3 — Customer APIs ✓
- Cart, checkout, orders, customers, reviews, favorites, promotions

## Phase 4 — Admin Panel ✓
- Dashboard, Products, Categories, Brands, Orders, Customers
- Warehouse, Analytics, POS, SMS logs

## Phase 5 — POS ✓
- Barcode scanning, receipt building, payment methods
- Suspended/resume/cancel, reprint receipt
- Auto-focus barcode input, Enter to add

## Phase 6 — Warehouse ✓
- Receiving, Suppliers, Write-Offs, Returns, Adjustments
- All inventory through StockMovement

## Phase 7 — Telegram Bot ✓
- Customer menu, order status, admin notifications

## Phase 8 — Customer Frontend ✓
- Home, Catalog, Product detail, Cart

## Phase 9 — Extensions ✓
- Normalized Color/Size, Barcode generation, Profit analytics
- Audit logging, Notification center

## Phase 10 — Production Readiness
- Performance optimization (indexed queries)
- Caching layer for catalog
- Rate limiting
- Monitoring / alerting
- Backup strategy
- Deployment scripts

## Future
- Multi-warehouse transfer workflows
- Purchase order management
- Supplier portal
- Customer mobile app
- Barcode label printing
- Advanced discount rules (BOGO, bundles)
- Gift cards
- Loyalty program automation
- Real-time dashboard websockets
- E2E tests

## Tech Debt
- Migrate frontend to TypeScript (optional)
- Add pagination metadata to all list endpoints
- Standardize error response format
- API versioning
