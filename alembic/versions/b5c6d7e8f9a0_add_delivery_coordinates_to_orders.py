"""add delivery coordinates to orders

Revision ID: b5c6d7e8f9a0
Revises: a3b4c5d6e7f8
Create Date: 2026-08-06 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c6d7e8f9a0'
down_revision: Union[str, None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('latitude', sa.Numeric(10, 7), nullable=True))
    op.add_column('orders', sa.Column('longitude', sa.Numeric(10, 7), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'longitude')
    op.drop_column('orders', 'latitude')