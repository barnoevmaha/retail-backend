from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.variant import ProductVariant
from app.models.product import Product
from app.models.receipt import Receipt
from app.repositories.company_repo import CompanyRepository
from app.repositories.setting_repo import SettingRepository

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


def _generate_receipt_html(receipt, items):
    qr_data = f"receipt/{receipt.id}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_data}"

    store_name = receipt.store_name or "Clothes Shop"
    store_address = receipt.store_address or ""
    store_phone = receipt.store_phone or ""
    store_tin = receipt.store_tin or ""
    store_line = store_address
    if store_phone:
        store_line += f" · {store_phone}"
    if store_tin:
        store_line += f" · TIN: {store_tin}"

    item_rows = ""
    for item in items:
        item_rows += f"""
        <tr>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;">{item.product_name or ''}<br><span style="font-size:10px;color:#999;">{item.barcode or ''}</span></td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:center;">{item.quantity}</td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:right;">${float(item.price):.2f}</td>
            <td style="padding:6px 8px;border-bottom:1px solid #ddd;text-align:right;">${float(item.price * item.quantity):.2f}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Receipt {receipt.receipt_number}</title>
<style>
  body {{ font-family: 'Courier New', monospace; font-size: 12px; width: 300px; margin: 0 auto; padding: 20px; }}
  h1 {{ text-align: center; font-size: 16px; margin-bottom: 2px; }}
  .store {{ text-align: center; font-size: 10px; color: #666; margin-bottom: 12px; }}
  .meta {{ font-size: 11px; margin-bottom: 12px; }}
  .meta div {{ padding: 1px 0; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 6px 8px; border-bottom: 2px solid #333; font-size: 10px; }}
  .total {{ font-size: 14px; font-weight: bold; text-align: right; margin-top: 8px; padding-top: 8px; border-top: 2px solid #333; }}
  .footer {{ text-align: center; margin-top: 16px; color: #999; font-size: 10px; }}
  .qr {{ text-align: center; margin-top: 12px; }}
  @media print {{ body {{ margin: 0; padding: 10px; }} .no-print {{ display: none; }} }}
</style></head><body>
<div class="no-print" style="text-align:center;margin-bottom:12px;">
  <button onclick="window.print()" style="padding:8px 24px;font-size:14px;">Print / Save PDF</button>
</div>
<h1>{store_name}</h1>
<div class="store">{store_line}</div>
<div class="meta">
  <div><strong>{receipt.receipt_number}</strong></div>
  <div>{receipt.created_at.strftime('%Y-%m-%d %H:%M') if receipt.created_at else ''}</div>
  <div>Payment: {receipt.payment_method or 'N/A'}</div>
  <div>Status: {receipt.status}</div>
  {('<div>Customer: ' + receipt.customer_name + '</div>') if receipt.customer_name else ''}
</div>
<table>
<tr><th>Item</th><th style="text-align:center;">Qty</th><th style="text-align:right;">Price</th><th style="text-align:right;">Total</th></tr>
{item_rows}
</table>
<div class="total">TOTAL: ${float(receipt.total_amount):.2f}</div>
<div class="qr"><img src="{qr_url}" width="80" height="80" alt="QR"></div>
<div class="footer">Thank you for your purchase!</div>
</body></html>"""


def _get_receipt_data(db, receipt_id: int):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        return None, None
    items = receipt.items
    return receipt, items


@router.get("/history")
def receipt_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin", "manager", "cashier")),
):
    receipts = db.query(Receipt).order_by(desc(Receipt.created_at)).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "receipt_number": r.receipt_number,
            "order_id": r.order_id,
            "customer_name": r.customer_name,
            "total": float(r.total_amount),
            "payment_method": r.payment_method,
            "status": r.status,
            "item_count": len(r.items),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in receipts
    ]


@router.get("/{receipt_id}")
def view_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt, items = _get_receipt_data(db, receipt_id)
    if not receipt:
        return HTMLResponse("<h1>Receipt not found</h1>", status_code=404)
    html = _generate_receipt_html(receipt, items)
    return HTMLResponse(content=html)


@router.get("/{receipt_id}/download")
def download_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt, items = _get_receipt_data(db, receipt_id)
    if not receipt:
        return HTMLResponse("<h1>Receipt not found</h1>", status_code=404)
    html = _generate_receipt_html(receipt, items)
    return HTMLResponse(
        content=html,
        headers={"Content-Disposition": f'attachment; filename="receipt-{receipt.receipt_number}.html"'},
    )
