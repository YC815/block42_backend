"""Level program model."""
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.level import Level


class LevelProgram(Base):
    """Stores per-user program commands for a level."""

    __tablename__ = "level_programs"
    __table_args__ = (
        UniqueConstraint("user_id", "level_id", name="uq_level_program_user_level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    level_id: Mapped[str] = mapped_column(
        ForeignKey("levels.id"), nullable=False, index=True
    )
    commands: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="programs")
    level: Mapped["Level"] = relationship("Level", back_populates="programs")

    @property
    def commands_f0(self) -> list[str]:
        return list(self.commands.get("commands_f0", []))

    @property
    def commands_f1(self) -> list[str]:
        return list(self.commands.get("commands_f1", []))

    @property
    def commands_f2(self) -> list[str]:
        return list(self.commands.get("commands_f2", []))
