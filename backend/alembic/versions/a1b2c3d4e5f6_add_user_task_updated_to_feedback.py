"""add user_id, task_id, updated_at to feedback

Revision ID: a1b2c3d4e5f6
Revises: 856099b92bd0
Create Date: 2026-09-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '856099b92bd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('feedback', sa.Column('user_id', sa.UUID(), nullable=True))
    op.add_column('feedback', sa.Column('task_id', sa.UUID(), nullable=True))
    op.add_column('feedback', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('feedback', 'updated_at')
    op.drop_column('feedback', 'task_id')
    op.drop_column('feedback', 'user_id')
