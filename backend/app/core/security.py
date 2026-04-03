"""
ClawHub 安全工具模块
包含 JWT 认证、密码哈希、权限验证等功能
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
http_bearer = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 令牌主题（通常是用户 ID）
        expires_delta: 过期时间增量
        extra_claims: 额外的声明
    
    Returns:
        JWT 令牌字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }
    
    if extra_claims:
        to_encode.update(extra_claims)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建刷新令牌
    
    Args:
        subject: 令牌主题（通常是用户 ID）
        expires_delta: 过期时间增量
    
    Returns:
        JWT 令牌字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码 JWT 令牌
    
    Args:
        token: JWT 令牌字符串
    
    Returns:
        解码后的令牌载荷，失败返回 None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(payload: dict, expected_type: str) -> bool:
    """验证令牌类型"""
    return payload.get("type") == expected_type


class TokenPayload:
    """令牌载荷数据类"""
    
    def __init__(self, payload: dict):
        self.sub: str = payload.get("sub", "")
        self.exp: int = payload.get("exp", 0)
        self.type: str = payload.get("type", "")
        self.extra: dict = {k: v for k, v in payload.items() 
                           if k not in ["sub", "exp", "type", "iat"]}
    
    @property
    def user_id(self) -> Optional[UUID]:
        """获取用户 ID"""
        try:
            return UUID(self.sub)
        except (ValueError, TypeError):
            return None
    
    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        return datetime.now(timezone.utc).timestamp() > self.exp


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions
    
    def __call__(self, user_permissions: list) -> bool:
        """检查用户是否有所有必需权限"""
        return all(perm in user_permissions for perm in self.required_permissions)


class RoleChecker:
    """角色检查器"""
    
    # 角色权限映射
    ROLE_PERMISSIONS = {
        "admin": [
            "user:read", "user:write", "user:delete",
            "lobster:read", "lobster:write", "lobster:delete",
            "org:read", "org:write", "org:delete",
            "comment:read", "comment:write", "comment:delete",
            "admin:full",
        ],
        "moderator": [
            "user:read",
            "lobster:read", "lobster:write", "lobster:delete",
            "comment:read", "comment:write", "comment:delete",
        ],
        "verified": [
            "user:read", "user:write",
            "lobster:read", "lobster:write",
            "org:read", "org:write",
            "comment:read", "comment:write",
        ],
        "user": [
            "user:read", "user:write",
            "lobster:read",
            "org:read",
            "comment:read", "comment:write",
        ],
        "guest": [
            "user:read",
            "lobster:read",
            "org:read",
            "comment:read",
        ],
    }
    
    @classmethod
    def get_permissions(cls, role: str) -> list:
        """获取角色的权限列表"""
        return cls.ROLE_PERMISSIONS.get(role, cls.ROLE_PERMISSIONS["guest"])
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """检查角色是否有指定权限"""
        return permission in cls.get_permissions(role)
    
    @classmethod
    def has_permissions(cls, role: str, permissions: list) -> bool:
        """检查角色是否有所有指定权限"""
        role_perms = set(cls.get_permissions(role))
        return all(perm in role_perms for perm in permissions)


def generate_password_reset_token(email: str) -> str:
    """生成密码重置令牌"""
    delta = timedelta(hours=24)
    now = datetime.now(timezone.utc)
    expires = now + delta
    encoded_jwt = jwt.encode(
        {"exp": expires, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """验证密码重置令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def generate_email_verification_token(email: str, user_id: UUID) -> str:
    """生成邮箱验证令牌"""
    delta = timedelta(hours=48)
    now = datetime.now(timezone.utc)
    expires = now + delta
    encoded_jwt = jwt.encode(
        {
            "exp": expires,
            "nbf": now,
            "sub": str(user_id),
            "email": email,
            "type": "email_verification",
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[tuple]:
    """验证邮箱验证令牌，返回 (user_id, email)"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        user_id = UUID(payload.get("sub"))
        email = payload.get("email")
        return user_id, email
    except (JWTError, ValueError):
        return None


# API Key 生成和管理
def generate_api_key() -> str:
    """生成 API Key"""
    import secrets
    return f"ch_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """哈希 API Key 用于存储"""
    return pwd_context.hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """验证 API Key"""
    return pwd_context.verify(plain_api_key, hashed_api_key)


# 安全响应头
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
