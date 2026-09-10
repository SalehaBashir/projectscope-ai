"""Phase 2: add organization_id to every tenant-owned table

Revision ID: f1a2b3c4d5e6
Revises: df3e8ca39815
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f1a2b3c4d5e6"
down_revision = "df3e8ca39815"
branch_labels = None
depends_on = None

# Tables that already carry project_id directly.
DIRECT_TABLES = [
    "features",
    "requirements",
    "risks",
    "estimates",
    "feedback",
    "tech_stack_recommendations",
    "theme_selections",
    "milestones",
    "predictions",
]


def upgrade():
    # 1. Tables with a direct project_id: add column, backfill, enforce NOT NULL.
    for table in DIRECT_TABLES:
        op.add_column(
            table,
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.execute(
            f"""
            UPDATE {table} t
            SET organization_id = p.organization_id
            FROM projects p
            WHERE t.project_id = p.id
            """
        )
        op.alter_column(table, "organization_id", nullable=False)
        op.create_index(f"ix_{table}_organization_id", table, ["organization_id"])

    # 2. tasks only has feature_id, so backfill via features -> projects.
    op.add_column(
        "tasks",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE tasks t
        SET organization_id = f.organization_id
        FROM features f
        WHERE t.feature_id = f.id
        """
    )
    op.alter_column("tasks", "organization_id", nullable=False)
    op.create_index("ix_tasks_organization_id", "tasks", ["organization_id"])

    # 3. llm_requests: project_id there is already nullable, so keep org_id nullable too.
    op.add_column(
        "llm_requests",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE llm_requests l
        SET organization_id = p.organization_id
        FROM projects p
        WHERE l.project_id = p.id
        """
    )
    op.create_index("ix_llm_requests_organization_id", "llm_requests", ["organization_id"])


def downgrade():
    op.drop_index("ix_llm_requests_organization_id", table_name="llm_requests")
    op.drop_column("llm_requests", "organization_id")

    op.drop_index("ix_tasks_organization_id", table_name="tasks")
    op.drop_column("tasks", "organization_id")

    for table in DIRECT_TABLES:
        op.drop_index(f"ix_{table}_organization_id", table_name=table)
        op.drop_column(table, "organization_id")