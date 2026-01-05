"""Admin API - 需 superuser 權限"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.level import Level, LevelStatus
from app.schemas.level import LevelApprove, LevelReject, LevelDetail, LevelListItem
from app.core.deps import require_superuser

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

    level.status = LevelStatus.PUBLISHED

    if data.as_official:
        level.is_official = True
        if data.official_order is not None:
            level.official_order = data.official_order
        else:
            max_order_result = db.query(Level.official_order).order_by(Level.official_order.desc()).first()
            level.official_order = (max_order_result[0] + 1) if max_order_result else 1
    else:
        level.is_official = False

    db.commit()
    db.refresh(level)
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

    Note:
        駁回原因 (reason) 目前未儲存，未來可擴充至 JSONB metadata
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")

    level.status = LevelStatus.REJECTED
    # 可以將 reason 存入 JSONB metadata（未來擴充）

    db.commit()
    db.refresh(level)
    return level
