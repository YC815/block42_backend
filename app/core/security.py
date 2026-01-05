"""安全工具：密碼雜湊、JWT token"""
from datetime import datetime, timedelta, UTC
from typing import Any
import bcrypt
from jose import jwt

from app.config import settings

# JWT 設定（從環境變數讀取）
SECRET_KEY = getattr(settings, "secret_key", "INSECURE_DEFAULT_SECRET_CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小時


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼

    Args:
        plain_password: 明文密碼
        hashed_password: Bcrypt 雜湊後的密碼

    Returns:
        bool: 密碼是否正確
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """雜湊密碼

    Args:
        password: 明文密碼（無長度限制）

    Returns:
        str: Bcrypt 雜湊後的密碼
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict[str, Any]) -> str:
    """建立 JWT token

    Args:
        data: Payload 資料（必須包含 'sub' 和 'is_superuser'）

    Returns:
        str: JWT token 字串
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
