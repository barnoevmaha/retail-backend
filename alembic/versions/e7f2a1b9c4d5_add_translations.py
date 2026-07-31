"""add translations

Revision ID: e7f2a1b9c4d5
Revises: c385a65dd399
Create Date: 2026-07-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f2a1b9c4d5'
down_revision: Union[str, None] = 'c385a65dd399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('translations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=500), nullable=False),
    sa.Column('en', sa.Text(), nullable=False),
    sa.Column('ru', sa.Text(), nullable=False),
    sa.Column('uz', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_translations_id'), 'translations', ['id'], unique=False)
    op.create_index(op.f('ix_translations_key'), 'translations', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_translations_key'), table_name='translations')
    op.drop_index(op.f('ix_translations_id'), table_name='translations')
    op.drop_table('translations')
