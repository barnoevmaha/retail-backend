"""backfill size_system for existing categories

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-08-07 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, None] = 'c6d7e8f9a0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


KEYWORDS = [
    ("apparel", ["shirt", "t-shirt", "tshirt", "tee", "sweatshirt", "sweat", "hoodie", "hoody", "jacket", "coat", "blazer", "top", "polo", "knitwear"]),
    ("trousers", ["trousers", "trouser", "jeans", "jean", "pants", "pant"]),
    ("shoes", ["shoes", "shoe", "sneaker", "boots", "boot", "sandals", "sandal", "loafers", "loafer"]),
    ("accessories", ["caps", "cap", "hat", "hats", "belt", "wallets", "wallet", "accessories", "accessory", "bags", "bag", "socks", "sock"]),
]


def _system_for(name: str, slug: str) -> str | None:
    haystack = " ".join([(name or "").lower(), (slug or "").lower()])
    for system, kws in KEYWORDS:
        if any(k in haystack for k in kws):
            return system
    return None


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, name, slug FROM categories WHERE size_system IS NULL")).fetchall()
    for row in rows:
        system = _system_for(row[1], row[2])
        if system:
            conn.execute(
                sa.text("UPDATE categories SET size_system = :sys WHERE id = :id"),
                {"sys": system, "id": row[0]},
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE categories SET size_system = NULL"))