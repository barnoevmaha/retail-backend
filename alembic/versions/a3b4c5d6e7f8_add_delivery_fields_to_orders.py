"""add delivery fields to orders

Revision ID: a3b4c5d6e7f8
Revises: f6a1b2c3d4e5
Create Date: 2026-08-06 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, None] = 'f6a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('customer_name', sa.String(length=255), nullable=True))
    op.add_column('orders', sa.Column('customer_phone', sa.String(length=50), nullable=True))
    op.add_column('orders', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('orders', sa.Column('address', sa.String(length=500), nullable=True))
    op.add_column('orders', sa.Column('apartment', sa.String(length=50), nullable=True))
    op.add_column('orders', sa.Column('delivery_note', sa.String(length=1000), nullable=True))
    op.add_column('orders', sa.Column('delivery_fee', sa.Numeric(12, 2), nullable=True, server_default='0'))


def downgrade() -> None:
    op.drop_column('orders', 'delivery_fee')
    op.drop_column('orders', 'delivery_note')
    op.drop_column('orders', 'apartment')
    op.drop_column('orders', 'address')
    op.drop_column('orders', 'city')
    op.drop_column('orders', 'customer_phone')
    op.drop_column('orders', 'customer_name')