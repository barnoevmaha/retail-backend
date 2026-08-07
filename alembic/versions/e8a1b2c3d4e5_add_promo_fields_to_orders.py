"""add promo discount fields to orders

Revision ID: e8a1b2c3d4e5
Revises: d7e8f9a0b1c2
Create Date: 2026-08-07

"""
from alembic import op
import sqlalchemy as sa

revision = "e8a1b2c3d4e5"
down_revision = "d7e8f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("orders", sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("orders", sa.Column("promo_code", sa.String(50), nullable=True))


def downgrade():
    op.drop_column("orders", "promo_code")
    op.drop_column("orders", "discount_amount")
