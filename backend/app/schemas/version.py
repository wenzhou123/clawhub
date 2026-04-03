"""
Version Schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class VersionBase(BaseModel):
    """版本基础 Schema"""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9-]+)?$", description="语义化版本号")
    description: Optional[str] = Field(None, max_length=1000, description="版本描述")


class VersionCreate(VersionBase):
    """创建版本"""
    pass


class VersionUpdate(BaseModel):
    """更新版本"""
    description: Optional[str] = None
    status: Optional[str] = None
    yanked_reason: Optional[str] = None


class VersionDependencyBase(BaseModel):
    """版本依赖基础 Schema"""
    dependency_type: str = Field(..., max_length=20, description="依赖类型: lobster, python, system")
    name: str = Field(..., max_length=100, description="依赖名称")
    version_constraint: Optional[str] = Field(None, max_length=100, description="版本约束")
    is_optional: bool = Field(False, description="是否为可选依赖")


class VersionDetail(VersionBase):
    """版本详情响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lobster_id: UUID
    revision: int
    status: str
    is_latest: bool
    file_size: int
    file_hash: str
    file_url: str
    config_content: Optional[dict] = None
    extra_metadata: Optional[dict] = None
    downloads_count: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class VersionListItem(VersionBase):
    """版本列表项响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version: str
    revision: int
    status: str
    is_latest: bool
    downloads_count: int
    created_at: datetime


class VersionResponse(VersionBase):
    """版本简洁响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lobster_id: UUID
    version: str
    revision: int
    status: str
    is_latest: bool
    file_size: int
    created_at: datetime
