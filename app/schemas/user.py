"""User Pydantic Schemas"""
from pydantic import BaseModel, Field


# --- Request Schemas ---
class UserRegister(BaseModel):
    """註冊使用者 Request"""
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱（3-50字）")
    password: str = Field(..., description="密碼")


class UserLogin(BaseModel):
    """登入 Request"""
    username: str
    password: str


# --- Response Schemas ---
class UserOut(BaseModel):
    """使用者資訊 Response（不含密碼）"""
    id: int
    username: str
    is_superuser: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT Token Response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT Token Payload（內部使用）"""
    user_id: int
    is_superuser: bool
