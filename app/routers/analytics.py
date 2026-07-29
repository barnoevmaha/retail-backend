from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, Date

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.customer import Customer
from app.models.category import Category
from app.models.brand import Brand
from app.models.color import Color
from app.models.size import Size
from app.models.stock_movement import StockMovement
from app.models.notification import Notification
from app.models.sms import SmsLog
from app.repositories.order_repo import OrderRepository

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _profit_query(db, statuses):
    return (
        db.query(
            func.sum(
                (ProductVariant.selling_price - ProductVariant.purchase_price) * OrderItem.quantity
            )
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(statuses))
    )


def _revenue_query(db, statuses):
    return (
        db.query(func.sum(OrderItem.price * OrderItem.quantity))
        .select_from(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(statuses))
    )


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    order_repo = OrderRepository(db)
    total_revenue = order_repo.revenue()
    total_orders = order_repo.count()
    total_customers = db.query(Customer).count()
    total_products = db.query(Product).count()

    total_profit = round(float(_profit_query(db, ["delivered", "ready"]).scalar() or 0), 2)
    margin = round((total_profit / total_revenue * 100), 1) if total_revenue else 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    delivered = ["delivered", "ready"]
    today_revenue = round(float(_revenue_query(db, delivered).filter(Order.created_at >= today_start).scalar() or 0), 2)
    today_profit = round(float(_profit_query(db, delivered).filter(Order.created_at >= today_start).scalar() or 0), 2)
    weekly_revenue = round(float(_revenue_query(db, delivered).filter(Order.created_at >= week_start).scalar() or 0), 2)
    monthly_revenue = round(float(_revenue_query(db, delivered).filter(Order.created_at >= month_start).scalar() or 0), 2)

    top_products = (
        db.query(
            Product.name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(
                (ProductVariant.selling_price - ProductVariant.purchase_price) * OrderItem.quantity
            ).label("total_profit"),
        )
        .join(ProductVariant, ProductVariant.product_id == Product.id)
        .join(OrderItem, OrderItem.variant_id == ProductVariant.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(["delivered", "ready"]))
        .group_by(Product.id, Product.name)
        .order_by(desc("total_sold"))
        .limit(10)
        .all()
    )

    low_stock = (
        db.query(ProductVariant)
        .filter(ProductVariant.quantity < 5, ProductVariant.is_active == True)
        .count()
    )

    out_of_stock = (
        db.query(ProductVariant)
        .filter(ProductVariant.quantity <= 0, ProductVariant.is_active == True)
        .count()
    )

    best_customers = (
        db.query(Customer)
        .order_by(desc(Customer.total_spent))
        .limit(10)
        .all()
    )

    popular_categories = (
        db.query(
            Category.name,
            func.count(Product.id).label("product_count"),
        )
        .join(Product, Product.category_id == Category.id)
        .filter(Product.is_active == True)
        .group_by(Category.id, Category.name)
        .order_by(desc("product_count"))
        .all()
    )

    popular_brands = (
        db.query(
            Brand.name,
            func.count(Product.id).label("product_count"),
        )
        .join(Product, Product.brand_id == Brand.id)
        .filter(Product.is_active == True)
        .group_by(Brand.id, Brand.name)
        .order_by(desc("product_count"))
        .all()
    )

    # fast moving: most sold in last 30 days
    fast_moving = (
        db.query(
            Product.name,
            func.sum(OrderItem.quantity).label("sold"),
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(["delivered", "ready"]), Order.created_at >= month_start)
        .group_by(Product.id, Product.name)
        .order_by(desc("sold"))
        .limit(10)
        .all()
    )

    # slow moving: products with no sales or very low sales
    slow_moving = (
        db.query(Product)
        .outerjoin(ProductVariant, ProductVariant.product_id == Product.id)
        .outerjoin(OrderItem, OrderItem.variant_id == ProductVariant.id)
        .outerjoin(Order, Order.id == OrderItem.order_id)
        .filter(Product.is_active == True)
        .group_by(Product.id)
        .having(
            func.coalesce(func.sum(OrderItem.quantity), 0) < 2
        )
        .limit(10)
        .all()
    )

    # recent activity
    recent_movements = (
        db.query(StockMovement)
        .order_by(desc(StockMovement.created_at))
        .limit(10)
        .all()
    )

    # notification alerts
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    failed_sms = db.query(SmsLog).filter(SmsLog.status == "failed").count()
    failed_notifications = db.query(Notification).filter(Notification.status == "failed").count()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": total_profit,
        "profit_margin": margin,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_products": total_products,
        "today_revenue": today_revenue,
        "today_profit": today_profit,
        "weekly_revenue": weekly_revenue,
        "monthly_revenue": monthly_revenue,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "pending_orders": pending_orders,
        "failed_sms": failed_sms,
        "failed_notifications": failed_notifications,
        "top_products": [
            {"name": p.name, "sold": int(p.total_sold), "profit": round(float(p.total_profit), 2)}
            for p in top_products
        ],
        "best_customers": [
            {"id": c.id, "name": f"{c.first_name} {c.last_name}", "spent": float(c.total_spent)}
            for c in best_customers
        ],
        "popular_categories": [{"name": cat.name, "count": int(cat.product_count)} for cat in popular_categories],
        "popular_brands": [{"name": b.name, "count": int(b.product_count)} for b in popular_brands],
        "fast_moving": [{"name": p.name, "sold": int(p.sold)} for p in fast_moving],
        "slow_moving": [{"id": p.id, "name": p.name, "slug": p.slug} for p in slow_moving],
        "recent_activity": [
            {
                "id": m.id,
                "variant_id": m.variant_id,
                "operation": m.operation,
                "quantity": m.quantity,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in recent_movements
        ],
    }


@router.get("/extended")
def extended_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager")),
):
    delivered = ["delivered", "ready"]

    sales_by_category = (
        db.query(
            Category.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Category, Category.id == Product.category_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(delivered))
        .group_by(Category.id, Category.name)
        .order_by(desc("total_revenue"))
        .all()
    )

    sales_by_brand = (
        db.query(
            Brand.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Brand, Brand.id == Product.brand_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(delivered))
        .group_by(Brand.id, Brand.name)
        .order_by(desc("total_revenue"))
        .all()
    )

    sales_by_size = (
        db.query(
            Size.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Size, Size.id == ProductVariant.size_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(delivered), ProductVariant.size_id.isnot(None))
        .group_by(Size.id, Size.name)
        .order_by(desc("total_qty"))
        .all()
    )

    sales_by_color = (
        db.query(
            Color.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
        )
        .select_from(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Color, Color.id == ProductVariant.color_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_(delivered), ProductVariant.color_id.isnot(None))
        .group_by(Color.id, Color.name)
        .order_by(desc("total_qty"))
        .all()
    )

    products_no_sales = (
        db.query(Product)
        .outerjoin(ProductVariant, ProductVariant.product_id == Product.id)
        .outerjoin(OrderItem, OrderItem.variant_id == ProductVariant.id)
        .outerjoin(Order, Order.id == OrderItem.order_id)
        .group_by(Product.id)
        .having(func.count(OrderItem.id) == 0)
        .all()
    )

    daily_sales = (
        db.query(
            cast(Order.created_at, Date).label("date"),
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(Order.total_amount).label("total_revenue"),
        )
        .select_from(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(delivered))
        .group_by(cast(Order.created_at, Date))
        .order_by(desc("date"))
        .limit(30)
        .all()
    )

    monthly_sales = (
        db.query(
            func.date_trunc("month", Order.created_at).label("month"),
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(Order.total_amount).label("total_revenue"),
        )
        .select_from(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(delivered))
        .group_by(func.date_trunc("month", Order.created_at))
        .order_by(desc("month"))
        .limit(12)
        .all()
    )

    return {
        "sales_by_category": [
            {"name": r.name, "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in sales_by_category
        ],
        "sales_by_brand": [
            {"name": r.name, "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in sales_by_brand
        ],
        "sales_by_size": [
            {"name": r.name, "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in sales_by_size
        ],
        "sales_by_color": [
            {"name": r.name, "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in sales_by_color
        ],
        "products_no_sales": [
            {"id": p.id, "name": p.name, "slug": p.slug} for p in products_no_sales
        ],
        "daily_sales": [
            {"date": str(r.date), "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in daily_sales
        ],
        "monthly_sales": [
            {"month": str(r.month), "qty": int(r.total_qty), "revenue": round(float(r.total_revenue), 2)}
            for r in monthly_sales
        ],
    }
