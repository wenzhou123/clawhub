"""
Search API Endpoints
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.lobster import LobsterListResponse
from app.services.search import SearchService

router = APIRouter()


@router.get("/lobsters", response_model=LobsterListResponse)
async def search_lobsters(
    q: Optional[str] = Query(None, min_length=1, description="搜索关键词"),
    tags: Optional[list] = Query(None, description="标签筛选"),
    namespace: Optional[str] = Query(None, description="命名空间"),
    sort: str = Query("relevance", regex="^(relevance|stars|downloads|updated_at|created_at)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """搜索 Lobsters"""
    service = SearchService(db)
    result = await service.search_lobsters(
        query=q,
        tags=tags,
        namespace=namespace,
        sort=sort,
        page=page,
        page_size=page_size,
        user_id=current_user.id if current_user else None,
    )
    return result


@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """搜索建议"""
    service = SearchService(db)
    suggestions = await service.get_suggestions(q, limit)
    return {"suggestions": suggestions}


@router.get("/trending")
async def trending_lobsters(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取趋势 Lobsters"""
    service = SearchService(db)
    result = await service.get_trending(period, limit)
    return result
