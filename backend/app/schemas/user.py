"""
ClawHub 用户相关 Schema
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus
from app.schemas.base import BaseSchema, TimestampIDSchema, PaginatedResponse


class UserBase(BaseSchema):
    """用户基础 Schema"""
    
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    display_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)


class UserCreate(UserBase):
    """用户创建 Schema"""
    
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """用户更新 Schema"""
    
    display_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    preferences: Optional[dict] = None


class UserResponse(TimestampIDSchema, UserBase):
    """用户响应 Schema（完整）"""
    
    role: UserRole
    status: UserStatus
    email_verified: bool
    is_superuser: bool
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]
    lobsters_count: int
    stars_received: int
    followers_count: int
    following_count: int


class UserProfile(UserResponse):
    """用户个人资料 Schema"""
    
    preferences: dict


class UserPublic(BaseSchema):
    """用户公开信息 Schema"""
    
    id: UUID
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    website: Optional[str]
    company: Optional[str]
    location: Optional[str]
    lobsters_count: int
    stars_received: int
    followers_count: int
    following_count: int
    created_at: datetime

    @field_validator("display_name", mode="before")
    @classmethod
    def default_display_name(cls, v, info):
        """如果没有显示名称，使用用户名"""
        if not v:
            return info.data.get("username")
        return v


# API Key Schemas
class APIKeyBase(BaseSchema):
    """API Key 基础 Schema"""
    
    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = Field(default_factory=list)


class APIKeyCreate(APIKeyBase):
    """API Key 创建 Schema"""
    
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365)


class APIKeyResponse(TimestampIDSchema, APIKeyBase):
    """API Key 响应 Schema"""
    
    user_id: UUID
    key_prefix: str = Field(..., description="API Key 前缀（仅显示前8位）")
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool


class APIKeyFullResponse(APIKeyResponse):
    """包含完整 API Key 的响应（仅创建时返回）"""
    
    key: str = Field(..., description="完整的 API Key（仅显示一次）")


# 认证相关 Schemas
class LoginRequest(BaseSchema):
    """登录请求 Schema"""
    
    username_or_email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseSchema):
    """令牌响应 Schema"""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="访问令牌过期时间（秒）")
    user: UserResponse


class RefreshTokenRequest(BaseSchema):
    """刷新令牌请求 Schema"""
    
    refresh_token: str


class PasswordResetRequest(BaseSchema):
    """密码重置请求 Schema"""
    
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """密码重置确认 Schema"""
    
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChangeRequest(BaseSchema):
    """密码修改请求 Schema"""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# 邮箱验证
class EmailVerificationRequest(BaseSchema):
    """邮箱验证请求 Schema"""
    
    email: EmailStr


class EmailVerificationConfirm(BaseSchema):
    """邮箱验证确认 Schema"""
    
    token: str


# 用户关注
class UserFollowRequest(BaseSchema):
    """关注用户请求 Schema"""
    
    username: str


class UserFollowResponse(BaseSchema):
    """关注响应 Schema"""
    
    follower_id: UUID
    following_id: UUID
    created_at: datetime


class UserFollowersResponse(BaseSchema):
    """用户关注者列表响应 Schema"""
    
    followers: PaginatedResponse[UserPublic]
    following: PaginatedResponse[UserPublic]


# 用户列表
class UserListResponse(PaginatedResponse[UserPublic]):
    """用户列表响应 Schema"""
    pass
