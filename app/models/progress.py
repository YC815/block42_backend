"""Level progress model."""
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.level import Level


class LevelProgress(Base):
    """Tracks per-user progress for a level."""

    __tablename__ = "level_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "level_id", name="uq_level_progress_user_level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    level_id: Mapped[str] = mapped_column(
        ForeignKey("levels.id"), nullable=False, index=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    best_steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stars_collected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="progresses")
    level: Mapped["Level"] = relationship("Level", back_populates="progresses")
