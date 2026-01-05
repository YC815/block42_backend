"""Public API - 無需認證"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.level import Level, LevelStatus
from app.schemas.level import LevelOut, LevelListItem

router = APIRouter(prefix="/levels", tags=["public"])


@router.get("/official", response_model=list[LevelListItem])
def list_official_levels(db: Session = Depends(get_db)):
    """列出官方關卡

    Args:
        db: 資料庫 session

    Returns:
        list[LevelListItem]: 官方關卡列表（按 official_order 排序）
    """
    levels = (
        db.query(Level)
        .filter(Level.is_official == True, Level.status == LevelStatus.PUBLISHED)
        .order_by(Level.official_order)
        .all()
    )
    return levels


@router.get("/community", response_model=list[LevelListItem])
def list_community_levels(db: Session = Depends(get_db)):
    """列出社群關卡

    Args:
        db: 資料庫 session

    Returns:
        list[LevelListItem]: 社群關卡列表（按建立時間倒序）
    """
    levels = (
        db.query(Level)
        .filter(Level.is_official == False, Level.status == LevelStatus.PUBLISHED)
        .order_by(Level.created_at.desc())
        .all()
    )
    return levels


@router.get("/{level_id}", response_model=LevelOut)
def get_level(level_id: str, db: Session = Depends(get_db)):
    """獲取單個關卡詳情（不含 solution）

    Args:
        level_id: 關卡 ID（NanoID）
        db: 資料庫 session

    Returns:
        LevelOut: 關卡詳情

    Raises:
        HTTPException 404: 關卡不存在
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="關卡不存在"
        )
    return level
