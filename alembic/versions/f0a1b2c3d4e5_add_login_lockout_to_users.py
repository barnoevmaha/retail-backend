"""add login lockout fields to users

Revision ID: f0a1b2c3d4e5
Revises: e8a1b2c3d4e5
Create Date: 2026-08-07

"""
from alembic import op
import sqlalchemy as sa

revision = "f0a1b2c3d4e5"
down_revision = "e8a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
