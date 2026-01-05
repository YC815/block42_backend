"""Level 模型 - 重構版"""
from datetime import datetime, UTC
from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
import enum

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class LevelStatus(str, enum.Enum):
    """關卡狀態

    狀態流轉：
    - CREATE → draft
    - UPDATE → draft (強制重置)
    - PUBLISH (一般使用者) → pending
    - PUBLISH (管理員) → published
    - APPROVE → published
    - REJECT → rejected
    """
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Level(Base):
    """關卡資料模型（重構版）

    使用 JSONB 儲存遊戲資料，避免過度正規化
    業務欄位提升為資料庫欄位，支援查詢與索引

    狀態機規則：
    - Create Level → status='draft', solution=NULL
    - Update Level → 強制 status='draft', solution=NULL
    - Publish (一般使用者) → status='pending'
    - Publish (管理員 + as_official) → status='published', is_official=True
    - Approve (管理員) → status='published'
    - Reject (管理員) → status='rejected'
    """
    __tablename__ = "levels"

    # ===== 業務欄位 =====
    id: Mapped[str] = mapped_column(String(12), primary_key=True)  # NanoID 12碼
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[LevelStatus] = mapped_column(
        Enum(LevelStatus),
        default=LevelStatus.DRAFT,
        nullable=False,
        index=True
    )
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    official_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ===== 遊戲資料 (JSONB) =====
    # map_data 結構: {start: {x, y, dir}, stars: [{x, y}], tiles: [{x, y, color}]}
    map_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # config 結構: {f0: int, f1: int, f2: int, tools: {paint_red, paint_green, paint_blue}}
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # ===== 驗證資料 (nullable) =====
    # solution 結構: {commands_f0: [str], commands_f1: [str], commands_f2: [str], steps_count: int}
    # Draft/Pending 狀態時為 NULL
    solution: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ===== 時間戳 =====
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    # ===== Relationship =====
    author: Mapped["User"] = relationship("User", back_populates="levels")
