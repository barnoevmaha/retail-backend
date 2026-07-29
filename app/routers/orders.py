from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.order import OrderItem
from app.models.variant import ProductVariant
from app.models.product import Product
from app.repositories.order_repo import OrderRepository
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("/")
def list_orders(
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = OrderService(db)
    if user.role == "customer":
        from app.repositories.customer_repo import CustomerRepository
        customer = CustomerRepository(db).get_by_user_id(user.id)
        if not customer:
            return {"items": [], "total": 0}
        orders = service.list_orders(customer_id=customer.id, skip=skip, limit=limit)
    else:
        orders = service.list_orders(status=status, skip=skip, limit=limit)
    return {
        "items": [OrderResponse.model_validate(o) for o in orders],
        "total": len(orders),
    }


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return OrderService(db).get_order(order_id)


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    return OrderService(db).update_status(order_id, body.status, user)


@router.get("/{order_id}/receipt", response_class=HTMLResponse)
def receipt(order_id: int, db: Session = Depends(get_db)):
    order = OrderService(db).get_order(order_id)
    items = (
        db.query(OrderItem)
        .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .filter(OrderItem.order_id == order_id)
        .all()
    )
    item_rows = ""
    for item in items:
        name = item.variant.product.name if item.variant and item.variant.product else f"Variant #{item.variant_id}"
        item_rows += f"""
        <tr>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;">{name}</td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:center;">{item.quantity}</td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:right;">${float(item.price):.2f}</td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:right;">${float(item.price * item.quantity):.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Receipt #{order.id}</title>
<style>
  body {{ font-family: 'Courier New', monospace; font-size: 13px; width: 300px; margin: 0 auto; padding: 20px; }}
  h1 {{ text-align: center; font-size: 18px; margin-bottom: 4px; }}
  .meta {{ text-align: center; color: #666; margin-bottom: 16px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 6px 8px; border-bottom: 2px solid #333; font-size: 12px; }}
  .total {{ font-size: 16px; font-weight: bold; text-align: right; margin-top: 12px; }}
  .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 11px; }}
  @media print {{ body {{ margin: 0; padding: 10px; }} }}
</style></head><body>
<h1>CLOTHES SHOP</h1>
<div class="meta">
  Receipt #{order.id}<br>
  {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else ''}<br>
  Payment: {order.payment_method or 'N/A'}<br>
  Status: {order.status}
</div>
<table>
<tr><th>Item</th><th style="text-align:center;">Qty</th><th style="text-align:right;">Price</th><th style="text-align:right;">Total</th></tr>
{item_rows}
</table>
<div class="total">TOTAL: ${float(order.total_amount):.2f}</div>
<div class="footer">Thank you for your purchase!</div>
<script>window.print()</script>
</body></html>"""
    return HTMLResponse(content=html)
