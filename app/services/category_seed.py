"""Seed missing standard categories on startup."""
from sqlalchemy.orm import Session

from app.models.category import Category

CATEGORIES = [
    {"slug": "shirts", "name": "Shirts, Polos & T-Shirts", "sort": 10},
    {"slug": "knitwear", "name": "Knitwear", "sort": 20},
    {"slug": "jackets-blazers-vests", "name": "Jackets, Blazers & Vests", "sort": 30},
    {"slug": "wallets", "name": "Wallets", "sort": 40},
    {"slug": "accessories", "name": "Accessories", "sort": 50},
    {"slug": "bags", "name": "Bags", "sort": 60},
    {"slug": "shoes", "name": "Shoes", "sort": 70},
    {"slug": "sweatshirts-hoodies", "name": "Sweatshirts & Hoodies", "sort": 80},
    {"slug": "hats-caps", "name": "Hats & Caps", "sort": 90},
    {"slug": "belts", "name": "Belts", "sort": 100},
    {"slug": "socks", "name": "Socks", "sort": 110},
    {"slug": "coats", "name": "Coats", "sort": 120},
    {"slug": "dresses-skirts", "name": "Dresses & Skirts", "sort": 130},
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