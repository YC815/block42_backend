"""關卡服務層 - CRUD 操作"""
from sqlalchemy.orm import Session
from nanoid import generate

from app.models.level import Level, LevelStatus
from app.schemas.level import LevelCreate, LevelUpdate, AdminLevelUpdate


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

    @staticmethod
    def admin_update_level(db: Session, level: Level, data: AdminLevelUpdate) -> Level:
        """管理員更新關卡（可部分更新）

        Args:
            db: 資料庫 session
            level: 要更新的關卡
            data: 更新資料

        Returns:
            Level: 更新後的關卡
        """
        updated_map = False

        if data.title is not None:
            level.title = data.title
        if data.map is not None:
            level.map_data = data.map.model_dump()
            updated_map = True
        if data.config is not None:
            level.config = data.config.model_dump()
            updated_map = True
        if data.is_official is not None:
            level.is_official = data.is_official
        if data.official_order is not None:
            level.official_order = data.official_order
        if data.status is not None:
            level.status = LevelStatus(data.status)

        if updated_map:
            level.solution = None
            if data.status is None:
                level.status = LevelStatus.DRAFT

        db.commit()
        db.refresh(level)
        return level
