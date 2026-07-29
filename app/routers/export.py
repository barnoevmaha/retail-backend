import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.models.stock_movement import StockMovement
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/export", tags=["export"])


def _export_response(rows: list[list], filename: str, format: str):
    filename = f"{filename}-{date.today()}"
    if format == "xlsx":
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return StreamingResponse(
            iter([buf.read()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'},
        )
    output = io.StringIO()
    writer = csv.writer(output)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
    )


@router.get("/products")
def export_products(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    rows = [["ID", "Name", "Slug", "Category", "Brand", "Variants"]]
    for p in products:
        cat = p.category.name if p.category else ""
        brand = p.brand.name if p.brand else ""
        rows.append([p.id, p.name, p.slug, cat, brand, len(p.variants)])
    return _export_response(rows, "products", format)


@router.get("/orders")
def export_orders(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(desc(Order.created_at)).all()
    rows = [["ID", "Date", "Customer", "Total", "Payment", "Status", "Items"]]
    for o in orders:
        cust = f"{o.customer.first_name} {o.customer.last_name}" if o.customer else ""
        rows.append([o.id, str(o.created_at.date()) if o.created_at else "", cust,
                     float(o.total_amount), o.payment_method or "", o.status, len(o.items)])
    return _export_response(rows, "orders", format)


@router.get("/customers")
def export_customers(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    customers = db.query(Customer).order_by(desc(Customer.total_spent)).all()
    rows = [["ID", "Name", "Phone", "Email", "Loyalty", "Orders", "Total Spent"]]
    for c in customers:
        rows.append([c.id, f"{c.first_name} {c.last_name}", c.phone or "", c.email or "",
                     c.loyalty_level or "", c.total_purchases, float(c.total_spent)])
    return _export_response(rows, "customers", format)


@router.get("/inventory")
def export_inventory(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "warehouse_employee")),
):
    variants = db.query(ProductVariant).filter(ProductVariant.is_active == True).all()
    rows = [["ID", "SKU", "Barcode", "Product", "Size", "Color", "Qty", "Purchase Price", "Selling Price"]]
    for v in variants:
        product_name = v.product.name if v.product else ""
        rows.append([v.id, v.sku, v.barcode, product_name, v.size or "", v.color or "",
                     v.quantity, float(v.purchase_price), float(v.selling_price)])
    return _export_response(rows, "inventory", format)


@router.get("/audit-logs")
def export_audit_logs(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(5000).all()
    rows = [["ID", "Date", "User", "Action", "Entity", "Entity ID"]]
    for l in logs:
        rows.append([l.id, str(l.created_at) if l.created_at else "", l.user_email or "",
                     l.action, l.entity, str(l.entity_id) if l.entity_id else ""])
    return _export_response(rows, "audit-logs", format)


@router.get("/sales")
def export_sales(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    q = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .filter(Order.status.in_(["delivered", "ready"]))
    )
    if from_date:
        q = q.filter(Order.created_at >= from_date)
    if to_date:
        q = q.filter(Order.created_at <= to_date)
    items = q.order_by(desc(Order.created_at)).limit(5000).all()
    rows = [["Order ID", "Date", "Product", "SKU", "Barcode", "Qty", "Price", "Total"]]
    for i in items:
        product_name = i.variant.product.name if i.variant and i.variant.product else ""
        rows.append([
            i.order_id, str(i.order.created_at.date()) if i.order and i.order.created_at else "",
            product_name, i.variant.sku if i.variant else "", i.variant.barcode if i.variant else "",
            i.quantity, float(i.price), float(i.price * i.quantity),
        ])
    return _export_response(rows, "sales", format)
