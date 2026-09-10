"""Phase 21: add assumptions and missing_information to projects

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-09-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b3c4d5e6f7a8"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column("assumptions", postgresql.JSONB, nullable=False, server_default="[]"),
    )
    op.add_column(
        "projects",
        sa.Column("missing_information", postgresql.JSONB, nullable=False, server_default="[]"),
    )


def downgrade():
    op.drop_column("projects", "missing_information")
    op.drop_column("projects", "assumptions")