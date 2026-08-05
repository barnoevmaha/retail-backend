"""Seed missing standard categories on startup."""
from sqlalchemy.orm import Session

from app.models.category import Category

CATEGORIES = [
    {"slug": "knitwear", "name": "Knitwear", "sort": 20},
    {"slug": "jackets-blazers-vests", "name": "Jackets, Blazers & Vests", "sort": 30},
    {"slug": "wallets", "name": "Wallets", "sort": 40},
    {"slug": "bags", "name": "Bags", "sort": 50},
    {"slug": "shoes", "name": "Shoes", "sort": 60},
]


def ensure_categories_seeded(db: Session) -> int:
    existing = {c.slug for c in db.query(Category).all()}
    added = 0
    for cat in CATEGORIES:
        if cat["slug"] in existing:
            continue
        db.add(Category(name=cat["name"], slug=cat["slug"], sort_order=cat["sort"]))
        added += 1
    return added