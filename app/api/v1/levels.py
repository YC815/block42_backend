"""Public API - 無需認證"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.level import Level, LevelStatus
from app.models.progress import LevelProgress
from app.models.program import LevelProgram
from app.schemas.progress import LevelProgressOut, LevelProgressUpdate
from app.schemas.program import LevelProgramOut, LevelProgramUpdate
from app.schemas.level import LevelOut, LevelListItem
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User

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
        .options(joinedload(Level.author))
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
        .options(joinedload(Level.author))
        .filter(Level.is_official == False, Level.status == LevelStatus.PUBLISHED)
        .order_by(Level.created_at.desc())
        .all()
    )
    return levels


@router.get("/progress", response_model=list[LevelProgressOut])
def list_level_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出目前使用者的關卡進度"""
    progress = (
        db.query(LevelProgress)
        .filter(LevelProgress.user_id == current_user.id)
        .all()
    )
    return progress


@router.put("/{level_id}/progress", response_model=LevelProgressOut)
def upsert_level_progress(
    level_id: str,
    data: LevelProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新或建立關卡進度"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="關卡不存在",
        )

    progress = (
        db.query(LevelProgress)
        .filter(
            LevelProgress.user_id == current_user.id,
            LevelProgress.level_id == level_id,
        )
        .first()
    )

    if not progress:
        progress = LevelProgress(
            user_id=current_user.id,
            level_id=level_id,
            is_completed=data.is_completed,
            best_steps=data.best_steps,
            stars_collected=data.stars_collected,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    if data.is_completed:
        progress.is_completed = True
    if data.best_steps is not None:
        progress.best_steps = (
            data.best_steps
            if progress.best_steps is None
            else min(progress.best_steps, data.best_steps)
        )
    if data.stars_collected is not None:
        progress.stars_collected = (
            data.stars_collected
            if progress.stars_collected is None
            else max(progress.stars_collected, data.stars_collected)
        )

    db.commit()
    db.refresh(progress)
    return progress


@router.get("/{level_id}/program", response_model=LevelProgramOut)
def get_level_program(
    level_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取得關卡程式碼"""
    program = (
        db.query(LevelProgram)
        .filter(
            LevelProgram.user_id == current_user.id,
            LevelProgram.level_id == level_id,
        )
        .first()
    )
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="程式尚未儲存",
        )
    return program


@router.put("/{level_id}/program", response_model=LevelProgramOut)
def upsert_level_program(
    level_id: str,
    data: LevelProgramUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新或建立關卡程式碼"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="關卡不存在",
        )

    program = (
        db.query(LevelProgram)
        .filter(
            LevelProgram.user_id == current_user.id,
            LevelProgram.level_id == level_id,
        )
        .first()
    )

    payload = {
        "commands_f0": data.commands_f0,
        "commands_f1": data.commands_f1,
        "commands_f2": data.commands_f2,
    }

    if not program:
        program = LevelProgram(
            user_id=current_user.id,
            level_id=level_id,
            commands=payload,
        )
        db.add(program)
        db.commit()
        db.refresh(program)
        return program

    program.commands = payload
    db.commit()
    db.refresh(program)
    return program


@router.get("/{level_id}", response_model=LevelOut)
def get_level(
    level_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """獲取單個關卡詳情（不含 solution）

    Args:
        level_id: 關卡 ID（NanoID）
        db: 資料庫 session
        current_user: 可選的當前使用者（公開端點）

    Returns:
        LevelOut: 關卡詳情（僅公開已發布關卡；草稿需作者或管理員）

    Raises:
        HTTPException 404/403: 關卡不存在或無權存取
    """
    level = (
        db.query(Level)
        .options(joinedload(Level.author))
        .filter(Level.id == level_id)
        .first()
    )
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="關卡不存在"
        )

    if level.status != LevelStatus.PUBLISHED:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要登入才能查看未發布的關卡"
            )
        if current_user.id != level.author_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權查看此關卡"
            )

    return level
