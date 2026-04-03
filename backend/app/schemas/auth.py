"""
Auth Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: Optional[UUID] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None


class UserRegister(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """用户登录"""
    username_or_email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=100)


class UserPasswordReset(BaseModel):
    """密码重置"""
    email: EmailStr


class UserPasswordChange(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class OAuthLogin(BaseModel):
    """OAuth 登录"""
    provider: str = Field(..., pattern=r"^(github|google|gitlab)$")
    code: str
    redirect_uri: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str
