"""Phase 6: add dependencies and source_requirement_id to features

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a2b3c4d5e6f7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "features",
        sa.Column("dependencies", postgresql.JSONB, nullable=False, server_default="[]"),
    )
    op.add_column(
        "features",
        sa.Column("source_requirement_id", postgresql.UUID(as_uuid=True), nullable=True),
    )


def downgrade():
    op.drop_column("features", "source_requirement_id")
    op.drop_column("features", "dependencies")