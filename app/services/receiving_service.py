from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.receiving import ReceivingItem
from app.models.user import User
from app.repositories.receiving_repo import ReceivingRepository
from app.repositories.variant_repo import VariantRepository
from app.services.stock_service import StockService


class ReceivingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReceivingRepository(db)
        self.variant_repo = VariantRepository(db)
        self.stock_service = StockService(db)

    def start(self, supplier_id: int | None, invoice_number: str | None, received_date: date | None, notes: str | None, user: User):
        if not received_date:
            received_date = date.today()
        return self.repo.create(
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            received_date=received_date,
            user_id=user.id,
            notes=notes,
            status="draft",
        )

    def add_item(self, receiving_id: int, variant_id: int, quantity: int, purchase_price: float):
        receiving = self.repo.get_by_id(receiving_id)
        if not receiving:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiving not found")
        if receiving.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add items to draft receivings")
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        return self.repo.add_item(receiving_id, variant_id, quantity, purchase_price)

    def add_item_by_barcode(self, receiving_id: int, barcode: str, quantity: int, purchase_price: float):
        variant = self.variant_repo.get_by_barcode(barcode)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variant with barcode '{barcode}' not found")
        return self.add_item(receiving_id, variant.id, quantity, purchase_price or float(variant.purchase_price))

    def create_variant_and_add(self, receiving_id: int, barcode: str, sku: str, product_id: int, size: str | None, color: str | None, quantity: int, purchase_price: float):
        receiving = self.repo.get_by_id(receiving_id)
        if not receiving:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiving not found")
        if receiving.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add items to draft receivings")
        if self.variant_repo.get_by_barcode(barcode):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Barcode already exists")
        if self.variant_repo.get_by_sku(sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
        variant = self.variant_repo.create(
            product_id=product_id,
            barcode=barcode,
            sku=sku,
            size=size,
            color=color,
            purchase_price=purchase_price,
            selling_price=purchase_price * 1.5,
        )
        return self.repo.add_item(receiving_id, variant.id, quantity, purchase_price)

    def confirm(self, receiving_id: int, user: User):
        receiving = self.repo.get_by_id(receiving_id)
        if not receiving:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiving not found")
        if receiving.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receiving already confirmed")
        items = self.db.query(ReceivingItem).filter(ReceivingItem.receiving_id == receiving_id).all()
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items to receive")

        for item in items:
            self.stock_service.receive(
                variant_id=item.variant_id,
                quantity=item.quantity,
                warehouse_id=None,
                user=user,
                reason=f"Receiving #{receiving_id} confirmed",
                document_number=receiving.invoice_number,
            )
        self.repo.update(receiving, status="confirmed")
        return {
            "id": receiving_id,
            "status": "confirmed",
            "items_count": len(items),
            "total_quantity": sum(i.quantity for i in items),
        }

    def cancel(self, receiving_id: int):
        receiving = self.repo.get_by_id(receiving_id)
        if not receiving:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiving not found")
        if receiving.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only cancel draft receivings")
        return self.repo.update(receiving, status="cancelled")

    def list_all(self, status: str | None = None, skip: int = 0, limit: int = 50):
        receivings = self.repo.list_all(status, skip, limit)
        result = []
        for r in receivings:
            supplier_name = r.supplier.company_name if r.supplier else ""
            result.append({
                "id": r.id,
                "supplier_name": supplier_name,
                "invoice_number": r.invoice_number,
                "received_date": r.received_date,
                "status": r.status,
                "items_count": len(r.items),
                "created_at": r.created_at,
            })
        return result

    def get_detail(self, receiving_id: int):
        receiving = self.repo.get_by_id(receiving_id)
        if not receiving:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiving not found")
        items = []
        for item in receiving.items:
            variant = self.variant_repo.get_by_id(item.variant_id)
            items.append({
                "id": item.id,
                "receiving_id": item.receiving_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "purchase_price": float(item.purchase_price),
                "barcode": variant.barcode if variant else "",
                "sku": variant.sku if variant else "",
            })
        supplier_name = receiving.supplier.company_name if receiving.supplier else ""
        return {
            "id": receiving.id,
            "supplier_id": receiving.supplier_id,
            "supplier_name": supplier_name,
            "invoice_number": receiving.invoice_number,
            "received_date": receiving.received_date,
            "status": receiving.status,
            "notes": receiving.notes,
            "items": items,
            "created_at": receiving.created_at,
        }
