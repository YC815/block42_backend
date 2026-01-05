"""add metadata column to levels

Revision ID: 725f279c1198
Revises: c68b56b73631
Create Date: 2026-01-05 21:55:19.640923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '725f279c1198'
down_revision: Union[str, Sequence[str], None] = 'c68b56b73631'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('levels', sa.Column('metadata', JSONB, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('levels', 'metadata')
