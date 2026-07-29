# API Endpoints

## Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/login | - | Login, returns JWT |
| POST | /api/auth/register | - | Register new user |
| GET | /api/auth/me | user | Current user info |

## Users
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/users/ | admin | List users |
| POST | /api/users/ | admin | Create user |
| PUT | /api/users/{id} | admin | Update user |
| DELETE | /api/users/{id} | admin | Delete user |

## Products
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/products/ | - | Search/list products |
| GET | /api/products/{slug} | - | Get product by slug |
| POST | /api/products/ | staff | Create product |
| PUT | /api/products/{id} | staff | Update product |
| DELETE | /api/products/{id} | admin | Delete product |

## Variants
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/variants/ | - | List/search variants |
| GET | /api/variants/barcode/{code} | - | Lookup by barcode |
| GET | /api/variants/{id} | - | Get variant |
| POST | /api/variants/ | staff | Create variant |
| PUT | /api/variants/{id} | staff | Update variant |

## Categories / Brands / Colors / Sizes
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | /api/categories/ | staff* | CRUD |
| GET/POST | /api/brands/ | staff* | CRUD |
| GET/POST | /api/colors/ | staff* | CRUD |
| GET/POST | /api/sizes/ | staff* | CRUD |

## Customer-Facing
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | /api/customers/ | staff | Customer CRUD |
| GET/POST | /api/cart/ | - | Cart operations |
| POST | /api/checkout/ | - | Place order |
| GET | /api/orders/ | user | List orders |
| GET | /api/orders/{id} | - | Order detail |
| PUT | /api/orders/{id}/status | staff | Update status |
| GET | /api/reviews/ | - | Product reviews |
| POST | /api/favorites/ | user | Toggle favorites |

## Warehouse / Inventory
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | /api/warehouse/ | admin | Warehouse CRUD |
| POST | /api/warehouse/receive | staff | Receive stock |
| POST | /api/warehouse/write-off | staff | Write off stock |
| POST | /api/warehouse/adjust | staff | Adjust stock |
| GET | /api/warehouse/movements | staff | Stock movements |
| GET | /api/inventory-history/ | staff | Full inventory history with joins |

## Operations Modules
| Module | Endpoints | Description |
|--------|-----------|-------------|
| Suppliers | /api/suppliers/ | CRUD |
| Receiving | /api/receiving/ | PO receiving with items |
| Returns | /api/returns/ | Customer returns |
| WriteOffs | /api/writeoffs/ | Stock write-offs |
| Adjustments | /api/adjustments/ | Inventory adjustments |
| Product Images | /api/product-images/ | Image management |

## Notifications
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/notifications/ | staff | List sent notifications |
| POST | /api/notifications/send | admin | Send notification via channel |
| PUT | /api/notifications/{id}/read | admin | Mark as read |

## POS Sessions
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/pos-sessions/ | staff | List suspended sales |
| GET | /api/pos-sessions/{id} | staff | Get session |
| POST | /api/pos-sessions/ | staff | Suspend sale |
| PUT | /api/pos-sessions/{id}/resume | staff | Resume sale |
| PUT | /api/pos-sessions/{id}/cancel | staff | Cancel suspended sale |

## Analytics
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/analytics/dashboard | staff | Dashboard KPIs |
| GET | /api/analytics/extended | staff | Advanced analytics |

## Audit Logs
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/audit-logs/ | admin | Filterable audit log |

## SMS
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/sms/send | admin | Send SMS |
| GET | /api/sms/logs | admin | SMS logs |
