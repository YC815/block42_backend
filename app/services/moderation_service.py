"""審核服務層 - 管理員審核操作"""
from typing import Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.level import Level, LevelStatus


class ModerationService:
    """審核業務邏輯服務"""

    @staticmethod
    def approve_level(
        db: Session,
        level: Level,
        as_official: bool = False,
        official_order: Optional[int] = None
    ) -> Level:
        """審核通過

        Args:
            db: 資料庫 session
            level: 待審核的關卡
            as_official: 是否設為官方關卡
            official_order: 官方關卡序號（可選）

        Returns:
            Level: 審核通過的關卡（status=PUBLISHED）

        Raises:
            ValueError: 如果關卡狀態不是 PENDING
        """
        if level.status != LevelStatus.PENDING:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"只能審核 PENDING 狀態的關卡，當前: {level.status}",
            )

        level.status = LevelStatus.PUBLISHED
        level.is_official = as_official

        if as_official:
            # 處理官方關卡序號
            if official_order is not None:
                level.official_order = official_order
            else:
                # 自動分配下一個序號
                max_order_result = db.query(Level.official_order).order_by(Level.official_order.desc()).first()
                level.official_order = (max_order_result[0] + 1) if max_order_result else 1

        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def reject_level(db: Session, level: Level, reason: str) -> Level:
        """駁回關卡

        Args:
            db: 資料庫 session
            level: 待審核的關卡
            reason: 駁回理由

        Returns:
            Level: 駁回的關卡（status=REJECTED）

        Raises:
            ValueError: 如果關卡狀態不是 PENDING
        """
        if level.status != LevelStatus.PENDING:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"只能駁回 PENDING 狀態的關卡，當前: {level.status}",
            )

        level.status = LevelStatus.REJECTED
        level.metadata_ = {
            "rejection_reason": reason,
            "rejected_at": datetime.now(UTC).isoformat()
        }

        db.commit()
        db.refresh(level)
        return level
