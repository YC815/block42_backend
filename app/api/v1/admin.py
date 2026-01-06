"""Admin API - 需 superuser 權限"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.level import Level, LevelStatus
from app.models.progress import LevelProgress
from app.models.program import LevelProgram
from app.schemas.level import (
    LevelApprove,
    LevelReject,
    LevelDetail,
    LevelListItem,
    AdminLevelListItem,
    AdminLevelUpdate,
)
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserOut
from app.schemas.admin import LevelTransferRequest, LevelTransferResult
from app.core.security import get_password_hash
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
        .options(joinedload(Level.author))
        .filter(Level.status == LevelStatus.PENDING)
        .order_by(Level.updated_at.desc())
        .all()
    )
    return levels


@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """列出所有使用者（管理用）"""
    users = db.query(User).order_by(User.id).all()
    return users


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: AdminUserCreate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """建立使用者（管理用）"""
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="使用者名稱已存在")

    user = User(
        username=data.username,
        hashed_password=get_password_hash(data.password),
        is_superuser=data.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """更新使用者（管理用）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

    if data.username and data.username != user.username:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="使用者名稱已存在")
        user.username = data.username

    if data.password:
        user.hashed_password = get_password_hash(data.password)

    if data.is_superuser is not None:
        user.is_superuser = data.is_superuser

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """刪除使用者（管理用）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能刪除自己")

    authored_count = (
        db.query(Level)
        .filter(Level.author_id == user_id)
        .count()
    )
    if authored_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="此帳號仍有關卡，請先刪除或轉移關卡",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

    db.query(LevelProgress).filter(LevelProgress.user_id == user_id).delete(
        synchronize_session=False
    )
    db.query(LevelProgram).filter(LevelProgram.user_id == user_id).delete(
        synchronize_session=False
    )

    db.delete(user)
    db.commit()
    return None


@router.post("/users/{user_id}/transfer-levels", response_model=LevelTransferResult)
def transfer_user_levels(
    user_id: int,
    payload: LevelTransferRequest,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):
    """批次轉移使用者關卡"""
    if not payload.transfers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供轉移資料")

    transfer_map = {item.level_id: item.new_author_id for item in payload.transfers}
    if any(target_id == user_id for target_id in transfer_map.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能轉移到原帳號",
        )

    target_ids = set(transfer_map.values())
    targets = db.query(User).filter(User.id.in_(target_ids)).all()
    if len(targets) != len(target_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目標帳號不存在",
        )

    levels = (
        db.query(Level)
        .filter(Level.id.in_(transfer_map.keys()), Level.author_id == user_id)
        .all()
    )
    if len(levels) != len(transfer_map):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="關卡不存在或不屬於該帳號",
        )

    for level in levels:
        level.author_id = transfer_map[level.id]

    db.commit()
    return LevelTransferResult(transferred=len(levels))


@router.get("/levels", response_model=list[AdminLevelListItem])
def list_all_levels(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """列出所有關卡（管理用）"""
    levels = (
        db.query(Level)
        .options(joinedload(Level.author))
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
    level = (
        db.query(Level)
        .options(joinedload(Level.author))
        .filter(Level.id == level_id)
        .first()
    )
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
