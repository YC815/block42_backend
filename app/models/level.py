"""SQLAlchemy 模型 - 單一資料表，JSONB 存所有配置"""
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Level(Base):
    """關卡資料模型

    使用 PostgreSQL JSONB 儲存完整配置，避免過度正規化

    data 結構：
    {
        "config": {"f0": 10, "f1": 0, "f2": 0, "tools": {...}},
        "map": {"start": {...}, "stars": [...], "tiles": [...]}
    }
    """
    __tablename__ = "levels"

    # 主鍵（使用 string 作為 ID，與 schema 一致）
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # 關卡標題
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # 所有配置資料（JSONB）
    # PostgreSQL 的 JSONB 支援索引、查詢，比拆表快
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
