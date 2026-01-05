"""User 模型"""
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database import Base

if TYPE_CHECKING:
    from app.models.level import Level


class User(Base):
    """使用者資料模型

    欄位：
    - id: 主鍵（自動遞增）
    - username: 使用者名稱（唯一）
    - hashed_password: Bcrypt 雜湊後的密碼
    - is_superuser: 是否為管理員
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship (反向關聯)
    levels: Mapped[list["Level"]] = relationship("Level", back_populates="author")
