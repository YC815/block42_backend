"""認證 API - 註冊、登入"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """註冊新使用者

    Args:
        user_data: 使用者註冊資料（username, password）
        db: 資料庫 session

    Returns:
        UserOut: 新建立的使用者資訊（不含密碼）

    Raises:
        HTTPException 400: 使用者名稱已存在
    """
    # 檢查 username 是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已存在"
        )

    # 建立使用者
    user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """登入取得 token

    Args:
        user_data: 登入資料（username, password）
        db: 資料庫 session

    Returns:
        Token: JWT access token

    Raises:
        HTTPException 401: 帳號或密碼錯誤
    """
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id, "is_superuser": user.is_superuser})
    return {"access_token": access_token, "token_type": "bearer"}
