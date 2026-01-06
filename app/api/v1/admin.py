"""Admin API - 需 superuser 權限"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.level import Level, LevelStatus
from app.schemas.level import (
    LevelApprove,
    LevelReject,
    LevelDetail,
    LevelListItem,
    AdminLevelListItem,
    AdminLevelUpdate,
)
from app.core.deps import require_superuser
from app.services import ModerationService, LevelService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/queue", response_model=list[LevelListItem])
def list_pending_levels(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """列出待審核關卡

    Args:
        current_user: 當前使用者（需為管理員）
        db: 資料庫 session

    Returns:
        list[LevelListItem]: 待審核關卡列表

    Requires:
        管理員權限
    """
    levels = (
        db.query(Level)
        .filter(Level.status == LevelStatus.PENDING)
        .order_by(Level.updated_at.desc())
        .all()
    )
    return levels


@router.get("/levels", response_model=list[AdminLevelListItem])
def list_all_levels(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """列出所有關卡（管理用）"""
    levels = (
        db.query(Level)
        .order_by(Level.updated_at.desc())
        .all()
    )
    return levels


@router.get("/levels/{level_id}", response_model=LevelDetail)
def get_level_admin(
    level_id: str,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """管理員獲取關卡詳情（含 solution）"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")
    return level


@router.put("/levels/{level_id}", response_model=LevelDetail)
def update_level_admin(
    level_id: str,
    data: AdminLevelUpdate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """管理員更新關卡（可部分更新）"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")

    level = LevelService.admin_update_level(db, level, data)
    return level


@router.delete("/levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_level_admin(
    level_id: str,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """管理員刪除關卡"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")

    LevelService.delete_level(db, level)
    return None


@router.post("/levels/{level_id}/approve", response_model=LevelDetail)
def approve_level(
    level_id: str,
    data: LevelApprove,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """審核通過

    **狀態機邏輯：**
    - as_official=True → status='published', is_official=True
    - as_official=False → status='published', is_official=False

    Args:
        level_id: 關卡 ID
        data: 審核資料（可選設為官方關卡）
        current_user: 當前使用者（需為管理員）
        db: 資料庫 session

    Returns:
        LevelDetail: 審核後的關卡

    Raises:
        HTTPException 404: 關卡不存在

    Requires:
        管理員權限
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")

    level = ModerationService.approve_level(db, level, data.as_official, data.official_order)
    return level


@router.post("/levels/{level_id}/reject", response_model=LevelDetail)
def reject_level(
    level_id: str,
    data: LevelReject,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """駁回關卡

    **狀態機邏輯：** status='rejected'

    Args:
        level_id: 關卡 ID
        data: 駁回理由
        current_user: 當前使用者（需為管理員）
        db: 資料庫 session

    Returns:
        LevelDetail: 駁回後的關卡

    Raises:
        HTTPException 404: 關卡不存在

    Requires:
        管理員權限
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")

    level = ModerationService.reject_level(db, level, data.reason)
    return level
