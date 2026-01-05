"""發布服務層 - 策略模式實現

使用策略模式消除狀態機的 if/elif 分支，符合開放封閉原則。
"""
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.level import Level, LevelStatus


class PublishStrategy(ABC):
    """發布策略抽象基類"""

    @abstractmethod
    def execute(self, db: Session, level: Level, solution: dict) -> Level:
        """執行發布策略

        Args:
            db: 資料庫 session
            level: 要發布的關卡
            solution: 解題資料

        Returns:
            Level: 發布後的關卡
        """
        pass


class AdminOfficialPublish(PublishStrategy):
    """管理員發布為官方關卡策略"""

    def __init__(self, official_order: Optional[int] = None):
        """初始化

        Args:
            official_order: 官方關卡序號（可選）
        """
        self.official_order = official_order

    def execute(self, db: Session, level: Level, solution: dict) -> Level:
        """執行官方關卡發布

        Args:
            db: 資料庫 session
            level: 要發布的關卡
            solution: 解題資料

        Returns:
            Level: status=PUBLISHED, is_official=True
        """
        level.status = LevelStatus.PUBLISHED
        level.is_official = True
        level.solution = solution

        # 處理 official_order
        if self.official_order is not None:
            level.official_order = self.official_order
        else:
            # 自動分配下一個序號
            max_order_result = db.query(Level.official_order).order_by(Level.official_order.desc()).first()
            level.official_order = (max_order_result[0] + 1) if max_order_result else 1

        db.commit()
        db.refresh(level)
        return level


class AdminCommunityPublish(PublishStrategy):
    """管理員發布為社群關卡策略"""

    def execute(self, db: Session, level: Level, solution: dict) -> Level:
        """執行社群關卡發布

        Args:
            db: 資料庫 session
            level: 要發布的關卡
            solution: 解題資料

        Returns:
            Level: status=PUBLISHED, is_official=False
        """
        level.status = LevelStatus.PUBLISHED
        level.is_official = False
        level.solution = solution
        db.commit()
        db.refresh(level)
        return level


class UserSubmitForReview(PublishStrategy):
    """一般使用者提交審核策略"""

    def execute(self, db: Session, level: Level, solution: dict) -> Level:
        """執行提交審核

        Args:
            db: 資料庫 session
            level: 要發布的關卡
            solution: 解題資料

        Returns:
            Level: status=PENDING（待審核）
        """
        level.status = LevelStatus.PENDING
        level.solution = solution
        db.commit()
        db.refresh(level)
        return level


def get_publish_strategy(
    user: User,
    as_official: bool = False,
    official_order: Optional[int] = None
) -> PublishStrategy:
    """工廠函數 - 根據用戶和參數返回對應策略

    這是唯一的條件分支集中點，策略類內部完全無條件。

    Args:
        user: 當前用戶
        as_official: 是否發布為官方關卡
        official_order: 官方關卡序號

    Returns:
        PublishStrategy: 對應的發布策略實例
    """
    if user.is_superuser:
        if as_official:
            return AdminOfficialPublish(official_order)
        else:
            return AdminCommunityPublish()
    else:
        return UserSubmitForReview()
