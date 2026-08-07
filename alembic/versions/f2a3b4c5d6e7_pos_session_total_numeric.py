"""pos_session total from Float to Numeric

Revision ID: f2a3b4c5d6e7
Revises: f0a1b2c3d4e5
Create Date: 2026-08-07

"""
from alembic import op
import sqlalchemy as sa

revision = "f2a3b4c5d6e7"
down_revision = "f0a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("pos_sessions", "total", existing_type=sa.Float(), type_=sa.Numeric(12, 2))


def downgrade():
    op.alter_column("pos_sessions", "total", existing_type=sa.Numeric(12, 2), type_=sa.Float())