"""FastAPI 依賴注入"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """從 JWT token 取得當前使用者

    Args:
        token: JWT token (自動從 Authorization header 提取)
        db: 資料庫 session

    Returns:
        User: 當前使用者物件

    Raises:
        HTTPException 401: Token 無效或使用者不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的認證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        is_superuser: bool = payload.get("is_superuser", False)

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, is_superuser=is_superuser)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    """要求 superuser 權限

    Args:
        current_user: 當前使用者（自動注入）

    Returns:
        User: 當前使用者物件

    Raises:
        HTTPException 403: 使用者不是管理員
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限"
        )
    return current_user
