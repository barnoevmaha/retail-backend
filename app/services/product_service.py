from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.product_repo import ProductRepository
from app.repositories.variant_repo import VariantRepository
from app.repositories.category_repo import CategoryRepository
from app.repositories.brand_repo import BrandRepository
from app.repositories.stock_repo import StockMovementRepository
from app.repositories.product_image_repo import ProductImageRepository
from app.repositories.color_repo import ColorRepository
from app.repositories.size_repo import SizeRepository
from app.models.user import User
from app.utils.barcode import generate_barcode
from app.utils.slug import unique_slug
from app.services.audit_service import AuditService


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.variant_repo = VariantRepository(db)
        self.category_repo = CategoryRepository(db)
        self.brand_repo = BrandRepository(db)
        self.stock_repo = StockMovementRepository(db)
        self.image_repo = ProductImageRepository(db)
        self.color_repo = ColorRepository(db)
        self.size_repo = SizeRepository(db)
        self.audit = AuditService(db)

    def search_products(self, q: str = "", category_id: int | None = None, brand_id: int | None = None, skip: int = 0, limit: int = 20):
        products = self.product_repo.search(q, category_id, brand_id, skip, limit)
        total = self.product_repo.count(q, category_id, brand_id)
        return products, total

    def get_product(self, slug: str):
        product = self.product_repo.get_by_slug(slug)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def get_product_with_images(self, slug: str):
        product = self.get_product(slug)
        images = self.image_repo.list_by_product(product.id)
        return product, images

    def create_product(self, data, user: User):
        payload = data.model_dump()
        payload["slug"] = unique_slug(
            payload["slug"], lambda s: self.product_repo.get_by_slug(s) is not None
        )
        product = self.product_repo.create(**payload)
        self.audit.log("create", "product", product.id, user, new_values=data.model_dump())
        return product

    def update_product(self, product_id: int, data, user: User | None = None):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        old = {"name": product.name, "slug": product.slug, "description": product.description, "is_active": product.is_active}
        new = data.model_dump(exclude_unset=True)

        def slug_free(s: str) -> bool:
            existing = self.product_repo.get_by_slug(s)
            return existing is None or existing.id == product.id

        if new.get("slug") is None:
            new.pop("slug", None)
        if new.get("slug"):
            new["slug"] = unique_slug(new["slug"], slug_free)
        updated = self.product_repo.update(product, **new)
        if user:
            self.audit.log("update", "product", product_id, user, old_values=old, new_values=new)
        return updated

    def delete_product(self, product_id: int, user: User | None = None):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        self.product_repo.delete(product)
        if user:
            self.audit.log("delete", "product", product_id, user, old_values={"name": product.name, "slug": product.slug})

    def get_variant_by_barcode(self, barcode: str):
        variant = self.variant_repo.get_by_barcode(barcode)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        return variant

    def create_variant(self, data, user: User | None = None):
        barcode = data.barcode or generate_barcode()
        sku = data.sku or barcode
        if self.variant_repo.get_by_barcode(barcode):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Barcode already exists")
        if sku != barcode and self.variant_repo.get_by_sku(sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
        variant_data = data.model_dump(exclude_unset=True)
        variant_data["barcode"] = barcode
        variant_data["sku"] = sku
        if data.color_id:
            color = self.color_repo.get_by_id(data.color_id)
            if color:
                variant_data["color"] = color.name
        if data.size_id:
            size = self.size_repo.get_by_id(data.size_id)
            if size:
                variant_data["size"] = size.name
        variant = self.variant_repo.create(**variant_data)
        if user:
            self.audit.log("create", "variant", variant.id, user, new_values=variant_data)
        return variant

    def update_variant(self, variant_id: int, data, user: User | None = None):
        variant = self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        old = {"barcode": variant.barcode, "sku": variant.sku, "selling_price": float(variant.selling_price),
               "purchase_price": float(variant.purchase_price), "quantity": variant.quantity}
        update_data = data.model_dump(exclude_unset=True)
        if "barcode" in update_data and update_data["barcode"] != variant.barcode:
            if self.variant_repo.get_by_barcode(update_data["barcode"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Barcode already exists")
        if "sku" in update_data and update_data["sku"] != variant.sku:
            if self.variant_repo.get_by_sku(update_data["sku"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
        if "color_id" in update_data and update_data.get("color_id"):
            color = self.color_repo.get_by_id(update_data["color_id"])
            if color:
                update_data["color"] = color.name
        if "size_id" in update_data and update_data.get("size_id"):
            size = self.size_repo.get_by_id(update_data["size_id"])
            if size:
                update_data["size"] = size.name
        updated = self.variant_repo.update(variant, **update_data)
        if user:
            self.audit.log("update", "variant", variant_id, user, old_values=old, new_values=update_data)
        return updated

    def add_image(self, product_id: int, image_url: str, sort_order: int = 0, is_main: bool = False):
        return self.image_repo.create(product_id, image_url, sort_order, is_main)

    def list_images(self, product_id: int):
        return self.image_repo.list_by_product(product_id)
