"""
ClawHub 自定义异常类
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class ClawHubException(HTTPException):
    """基础自定义异常"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: str = "UNKNOWN_ERROR",
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class AuthenticationError(ClawHubException):
    """认证错误"""
    
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(ClawHubException):
    """授权错误"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundError(ClawHubException):
    """资源不存在错误"""
    
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ValidationError(ClawHubException):
    """验证错误"""
    
    def __init__(self, detail: Any = "验证失败"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class ConflictError(ClawHubException):
    """冲突错误"""
    
    def __init__(self, detail: str = "资源已存在"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT_ERROR",
        )


class RateLimitError(ClawHubException):
    """速率限制错误"""
    
    def __init__(self, detail: str = "请求过于频繁", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)},
            error_code="RATE_LIMIT_EXCEEDED",
        )
        self.retry_after = retry_after


class StorageError(ClawHubException):
    """存储错误"""
    
    def __init__(self, detail: str = "存储操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="STORAGE_ERROR",
        )


class DatabaseError(ClawHubException):
    """数据库错误"""
    
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
        )


class ExternalServiceError(ClawHubException):
    """外部服务错误"""
    
    def __init__(self, detail: str = "外部服务调用失败"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
        )


class LobsterNotFoundError(NotFoundError):
    """Lobster 不存在错误"""
    
    def __init__(self, lobster_id: Optional[str] = None):
        detail = f"Lobster {lobster_id} 不存在" if lobster_id else "Lobster 不存在"
        super().__init__(detail=detail)
        self.error_code = "LOBSTER_NOT_FOUND"


class VersionNotFoundError(NotFoundError):
    """版本不存在错误"""
    
    def __init__(self, version: Optional[str] = None):
        detail = f"版本 {version} 不存在" if version else "版本不存在"
        super().__init__(detail=detail)
        self.error_code = "VERSION_NOT_FOUND"


class UserNotFoundError(NotFoundError):
    """用户不存在错误"""
    
    def __init__(self, username: Optional[str] = None):
        detail = f"用户 {username} 不存在" if username else "用户不存在"
        super().__init__(detail=detail)
        self.error_code = "USER_NOT_FOUND"


class OrganizationNotFoundError(NotFoundError):
    """组织不存在错误"""
    
    def __init__(self, org_name: Optional[str] = None):
        detail = f"组织 {org_name} 不存在" if org_name else "组织不存在"
        super().__init__(detail=detail)
        self.error_code = "ORGANIZATION_NOT_FOUND"


class InvalidCredentialsError(AuthenticationError):
    """无效凭证错误"""
    
    def __init__(self, detail: str = "用户名或密码错误"):
        super().__init__(detail=detail)
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """令牌过期错误"""
    
    def __init__(self, detail: str = "令牌已过期"):
        super().__init__(detail=detail)
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """无效令牌错误"""
    
    def __init__(self, detail: str = "无效的令牌"):
        super().__init__(detail=detail)
        self.error_code = "INVALID_TOKEN"


class DuplicateUserError(ConflictError):
    """重复用户错误"""
    
    def __init__(self, field: str = "用户名或邮箱"):
        super().__init__(detail=f"{field} 已被注册")
        self.error_code = "DUPLICATE_USER"


class DuplicateLobsterError(ConflictError):
    """重复 Lobster 错误"""
    
    def __init__(self, name: Optional[str] = None):
        detail = f"Lobster {name} 已存在" if name else "Lobster 已存在"
        super().__init__(detail=detail)
        self.error_code = "DUPLICATE_LOBSTER"


class DuplicateOrganizationError(ConflictError):
    """重复组织错误"""
    
    def __init__(self, name: Optional[str] = None):
        detail = f"组织 {name} 已存在" if name else "组织已存在"
        super().__init__(detail=detail)
        self.error_code = "DUPLICATE_ORGANIZATION"


class FileTooLargeError(ValidationError):
    """文件过大错误"""
    
    def __init__(self, max_size: int):
        super().__init__(detail=f"文件大小超过限制 ({max_size // 1024 // 1024}MB)")
        self.error_code = "FILE_TOO_LARGE"


class InvalidFileTypeError(ValidationError):
    """无效文件类型错误"""
    
    def __init__(self, allowed_types: list):
        super().__init__(detail=f"仅支持以下文件类型: {', '.join(allowed_types)}")
        self.error_code = "INVALID_FILE_TYPE"


class QuotaExceededError(ClawHubException):
    """配额超限错误"""
    
    def __init__(self, resource: str = "资源"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{resource} 配额已超限",
            error_code="QUOTA_EXCEEDED",
        )
