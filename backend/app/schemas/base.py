"""
ClawHub 基础 Schema 模块
"""
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """基础 Schema 类"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """带时间戳的 Schema"""
    
    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """带 ID 的 Schema"""
    
    id: UUID


class TimestampIDSchema(IDSchema, TimestampSchema):
    """带 ID 和时间戳的 Schema"""
    pass


class PaginationParams(BaseSchema):
    """分页参数 Schema"""
    
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """分页响应 Schema"""
    
    items: List[T]
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class SortParams(BaseSchema):
    """排序参数 Schema"""
    
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")


class ErrorDetail(BaseSchema):
    """错误详情 Schema"""
    
    field: Optional[str] = Field(default=None, description="错误字段")
    message: str = Field(description="错误信息")
    code: Optional[str] = Field(default=None, description="错误代码")


class ErrorResponse(BaseSchema):
    """错误响应 Schema"""
    
    error_code: str = Field(description="错误代码")
    message: str = Field(description="错误消息")
    details: Optional[List[ErrorDetail]] = Field(default=None, description="详细错误信息")
    request_id: Optional[str] = Field(default=None, description="请求 ID")


class SuccessResponse(BaseSchema):
    """成功响应 Schema"""
    
    success: bool = True
    message: str = Field(default="操作成功")
    data: Optional[dict] = None


class HealthCheckResponse(BaseSchema):
    """健康检查响应 Schema"""
    
    status: str = Field(description="服务状态")
    version: str = Field(description="服务版本")
    timestamp: datetime = Field(description="检查时间")
    services: dict = Field(default_factory=dict, description="依赖服务状态")


class AuditLogBase(BaseSchema):
    """审计日志基础 Schema"""
    
    action: str
    target_type: str
    target_id: Optional[UUID] = None
    description: Optional[str] = None


class AuditLogResponse(TimestampIDSchema, AuditLogBase):
    """审计日志响应 Schema"""
    
    user_id: Optional[UUID]
    user_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    is_success: bool
    error_message: Optional[str]


# 文件上传相关
class FileUploadResponse(BaseSchema):
    """文件上传响应 Schema"""
    
    filename: str
    url: str
    size: int
    content_type: str
    hash: Optional[str] = None
