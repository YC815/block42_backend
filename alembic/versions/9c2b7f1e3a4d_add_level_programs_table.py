"""add level programs table

Revision ID: 9c2b7f1e3a4d
Revises: 8f2a3b1c4d5e
Create Date: 2026-01-06 10:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "9c2b7f1e3a4d"
down_revision: Union[str, Sequence[str], None] = "8f2a3b1c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "level_programs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level_id", sa.String(length=12), nullable=False),
        sa.Column("commands", JSONB, nullable=False),
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
        sa.UniqueConstraint("user_id", "level_id", name="uq_level_program_user_level"),
    )
    op.create_index("ix_level_programs_user_id", "level_programs", ["user_id"], unique=False)
    op.create_index("ix_level_programs_level_id", "level_programs", ["level_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_level_programs_level_id", table_name="level_programs")
    op.drop_index("ix_level_programs_user_id", table_name="level_programs")
    op.drop_table("level_programs")
