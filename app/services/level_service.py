"""關卡服務層 - CRUD 操作"""
from sqlalchemy.orm import Session
from nanoid import generate

from app.models.level import Level, LevelStatus
from app.schemas.level import LevelCreate, LevelUpdate


class LevelService:
    """關卡業務邏輯服務"""

    @staticmethod
    def create_level(db: Session, author_id: int, data: LevelCreate) -> Level:
        """建立新關卡

        Args:
            db: 資料庫 session
            author_id: 作者 ID
            data: 關卡資料

        Returns:
            Level: 新建立的關卡（status=DRAFT）
        """
        level = Level(
            id=generate(size=12),  # NanoID 12碼
            author_id=author_id,
            title=data.title,
            status=LevelStatus.DRAFT,
            is_official=False,
            official_order=0,
            map_data=data.map.model_dump(),
            config=data.config.model_dump(),
            solution=None
        )
        db.add(level)
        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def update_level(db: Session, level: Level, data: LevelUpdate) -> Level:
        """更新關卡（強制回到 DRAFT 狀態）

        Args:
            db: 資料庫 session
            level: 要更新的關卡
            data: 更新資料

        Returns:
            Level: 更新後的關卡（status=DRAFT, solution=NULL）
        """
        level.title = data.title
        level.map_data = data.map.model_dump()
        level.config = data.config.model_dump()
        level.status = LevelStatus.DRAFT
        level.solution = None
        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def delete_level(db: Session, level: Level) -> None:
        """刪除關卡

        Args:
            db: 資料庫 session
            level: 要刪除的關卡
        """
        db.delete(level)
        db.commit()
