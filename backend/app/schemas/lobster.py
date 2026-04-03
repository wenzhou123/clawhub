"""
Lobster Schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class LobsterBase(BaseModel):
    """Lobster 基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Lobster 名称")
    description: Optional[str] = Field(None, max_length=5000, description="描述")
    readme: Optional[str] = Field(None, description="README 内容")
    is_public: bool = Field(True, description="是否公开")


class LobsterCreate(LobsterBase):
    """创建 Lobster"""
    namespace: Optional[str] = Field(None, description="命名空间（用户名或组织名）")
    tags: List[str] = Field(default=[], max_length=10, description="标签列表")


class LobsterUpdate(BaseModel):
    """更新 Lobster"""
    description: Optional[str] = Field(None, max_length=5000)
    readme: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class LobsterVersionBase(BaseModel):
    """版本基础信息"""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$", description="语义化版本")
    description: Optional[str] = Field(None, max_length=1000)
    

class LobsterVersionCreate(LobsterVersionBase):
    """创建版本"""
    pass


class LobsterVersionResponse(LobsterVersionBase):
    """版本响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    lobster_id: UUID
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    download_count: int = 0
    created_at: datetime
    

class LobsterResponse(LobsterBase):
    """Lobster 响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    namespace: str
    slug: str
    full_name: str
    owner_id: UUID
    owner_username: str
    owner_avatar: Optional[str] = None
    tags: List[str] = []
    star_count: int = 0
    download_count: int = 0
    version_count: int = 0
    latest_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    

class LobsterDetailResponse(LobsterResponse):
    """Lobster 详情响应"""
    versions: List[LobsterVersionResponse] = []
    is_starred: bool = False
    permissions: dict = {}


class LobsterListResponse(BaseModel):
    """Lobster 列表响应"""
    total: int
    items: List[LobsterResponse]
    page: int
    page_size: int


class LobsterSearchQuery(BaseModel):
    """搜索参数"""
    q: Optional[str] = Field(None, description="搜索关键词")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    namespace: Optional[str] = Field(None, description="命名空间筛选")
    sort: str = Field("updated_at", pattern=r"^(created_at|updated_at|stars|downloads|name)$")
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
