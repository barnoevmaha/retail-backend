"""add color_id to product_images

Revision ID: f6a1b2c3d4e5
Revises: a1b2c3d4e5f6
Create Date: 2026-08-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a1b2c3d4e5'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('product_images', sa.Column('color_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_product_images_color', 'product_images', 'colors', ['color_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_product_images_color', 'product_images', type_='foreignkey')
    op.drop_column('product_images', 'color_id')
