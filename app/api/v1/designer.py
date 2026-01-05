"""Designer API - 需認證"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.level import Level
from app.schemas.level import (
    LevelCreate,
    LevelUpdate,
    LevelPublish,
    LevelDetail,
    LevelListItem,
)
from app.core.deps import get_current_user
from app.services import LevelService, get_publish_strategy

router = APIRouter(prefix="/designer", tags=["designer"])


@router.get("/levels", response_model=list[LevelListItem])
def list_my_levels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出當前使用者的所有關卡

    Args:
        current_user: 當前使用者（自動注入）
        db: 資料庫 session

    Returns:
        list[LevelListItem]: 使用者的關卡列表（含所有狀態）
    """
    levels = (
        db.query(Level)
        .filter(Level.author_id == current_user.id)
        .order_by(Level.updated_at.desc())
        .all()
    )
    return levels


@router.post("/levels", response_model=LevelDetail, status_code=status.HTTP_201_CREATED)
def create_level(
    data: LevelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """建立新關卡（狀態 = draft）

    Args:
        data: 關卡資料
        current_user: 當前使用者（自動注入）
        db: 資料庫 session

    Returns:
        LevelDetail: 新建立的關卡
    """
    level = LevelService.create_level(db, current_user.id, data)
    return level


@router.put("/levels/{level_id}", response_model=LevelDetail)
def update_level(
    level_id: str,
    data: LevelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新關卡（強制回到 draft）

    **狀態機規則：任何修改都會強制 status='draft', solution=NULL**

    Args:
        level_id: 關卡 ID
        data: 更新資料
        current_user: 當前使用者（自動注入）
        db: 資料庫 session

    Returns:
        LevelDetail: 更新後的關卡

    Raises:
        HTTPException 404: 關卡不存在
        HTTPException 403: 無權修改此關卡
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")
    if level.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="無權修改此關卡")

    level = LevelService.update_level(db, level, data)
    return level


@router.post("/levels/{level_id}/publish", response_model=LevelDetail)
def publish_level(
    level_id: str,
    data: LevelPublish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """發布關卡（提交 solution）

    **狀態機邏輯：**
    - 一般使用者 → status='pending' (需審核)
    - 管理員 + as_official=True → status='published', is_official=True
    - 管理員 + as_official=False → status='published', is_official=False

    Args:
        level_id: 關卡 ID
        data: 發布資料（含 solution）
        current_user: 當前使用者（自動注入）
        db: 資料庫 session

    Returns:
        LevelDetail: 發布後的關卡

    Raises:
        HTTPException 404: 關卡不存在
        HTTPException 403: 無權發布此關卡
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")
    if level.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="無權發布此關卡")

    # 使用策略模式 - 消除所有 if/elif 分支
    strategy = get_publish_strategy(current_user, data.as_official, data.official_order)
    level = strategy.execute(db, level, data.solution.model_dump())
    return level


@router.delete("/levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_level(
    level_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刪除關卡（只能刪自己的）

    Args:
        level_id: 關卡 ID
        current_user: 當前使用者（自動注入）
        db: 資料庫 session

    Raises:
        HTTPException 404: 關卡不存在
        HTTPException 403: 無權刪除此關卡
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="關卡不存在")
    if level.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="無權刪除此關卡")

    LevelService.delete_level(db, level)
    return None
