"""
Tags API Endpoints
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.search import SearchService

router = APIRouter()


@router.get("/popular")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取热门标签"""
    service = SearchService(db)
    tags = await service.get_popular_tags(limit)
    return {"items": tags}


@router.get("/{tag}/lobsters")
async def get_tag_lobsters(
    tag: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取标签下的 Lobsters"""
    from app.services.lobster import LobsterService
    
    service = LobsterService(db)
    result = await service.list_lobsters(
        tag=tag,
        page=page,
        page_size=page_size,
    )
    return result
