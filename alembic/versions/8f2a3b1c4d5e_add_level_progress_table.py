"""add level progress table

Revision ID: 8f2a3b1c4d5e
Revises: 725f279c1198
Create Date: 2026-01-06 10:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f2a3b1c4d5e"
down_revision: Union[str, Sequence[str], None] = "725f279c1198"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "level_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level_id", sa.String(length=12), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("best_steps", sa.Integer(), nullable=True),
        sa.Column("stars_collected", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["level_id"], ["levels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "level_id", name="uq_level_progress_user_level"),
    )
    op.create_index("ix_level_progress_user_id", "level_progress", ["user_id"], unique=False)
    op.create_index("ix_level_progress_level_id", "level_progress", ["level_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_level_progress_level_id", table_name="level_progress")
    op.drop_index("ix_level_progress_user_id", table_name="level_progress")
    op.drop_table("level_progress")
