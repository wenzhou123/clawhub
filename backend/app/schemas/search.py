"""
Search Schemas
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.lobster import LobsterResponse


class SearchRequest(BaseModel):
    """搜索请求"""
    q: Optional[str] = Field(None, description="搜索关键词")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    namespace: Optional[str] = Field(None, description="命名空间筛选")
    owner: Optional[str] = Field(None, description="所有者用户名筛选")
    sort: str = Field("updated_at", pattern=r"^(created_at|updated_at|stars|downloads|name)$", description="排序字段")
    order: str = Field("desc", pattern=r"^(asc|desc)$", description="排序方向")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class SearchFilters(BaseModel):
    """搜索聚合筛选结果"""
    tags: List[str] = Field(default_factory=list, description="可用标签")
    namespaces: List[str] = Field(default_factory=list, description="可用命名空间")


class SearchResponse(BaseModel):
    """搜索响应"""
    total: int = Field(..., description="总结果数")
    items: List[LobsterResponse] = Field(default_factory=list, description="结果列表")
    filters: SearchFilters = Field(..., description="筛选选项")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")
