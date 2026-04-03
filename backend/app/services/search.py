"""
Search Service
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lobster import Lobster


class SearchService:
    """搜索服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_lobsters(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        sort: str = "relevance",
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[str] = None,
    ) -> dict:
        """搜索 Lobsters"""
        sql = select(Lobster).where(Lobster.is_deleted == False)
        
        # Visibility filter
        if user_id:
            sql = sql.where(
                (Lobster.is_public == True) | (Lobster.owner_id == user_id)
            )
        else:
            sql = sql.where(Lobster.is_public == True)
        
        # Text search
        if query:
            search_filter = or_(
                Lobster.name.ilike(f"%{query}%"),
                Lobster.description.ilike(f"%{query}%"),
                Lobster.readme.ilike(f"%{query}%"),
                Lobster.tags.contains([query]),
            )
            sql = sql.where(search_filter)
        
        # Tag filter
        if tags:
            for tag in tags:
                sql = sql.where(Lobster.tags.contains([tag]))
        
        # Namespace filter
        if namespace:
            sql = sql.where(Lobster.namespace == namespace)
        
        # Sort
        if sort == "relevance":
            # TODO: Implement relevance scoring
            sql = sql.order_by(desc(Lobster.star_count))
        elif sort == "stars":
            sql = sql.order_by(desc(Lobster.star_count))
        elif sort == "downloads":
            sql = sql.order_by(desc(Lobster.download_count))
        elif sort == "updated_at":
            sql = sql.order_by(desc(Lobster.updated_at))
        elif sort == "created_at":
            sql = sql.order_by(desc(Lobster.created_at))
        
        # Pagination
        total_result = await self.db.execute(
            select(func.count()).select_from(sql.subquery())
        )
        total = total_result.scalar()
        
        sql = sql.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(sql)
        items = result.scalars().all()
        
        return {
            "total": total,
            "items": list(items),
            "page": page,
            "page_size": page_size,
        }
    
    async def get_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """获取搜索建议"""
        # Search in names
        result = await self.db.execute(
            select(Lobster.name)
            .where(
                Lobster.is_deleted == False,
                Lobster.is_public == True,
                Lobster.name.ilike(f"%{query}%"),
            )
            .limit(limit)
        )
        names = [row[0] for row in result.all()]
        
        # Search in tags
        # TODO: Implement tag-based suggestions
        
        return names
    
    async def get_trending(self, period: str = "week", limit: int = 10) -> dict:
        """获取趋势"""
        # Calculate date range
        now = datetime.utcnow()
        if period == "day":
            since = now - timedelta(days=1)
        elif period == "week":
            since = now - timedelta(weeks=1)
        elif period == "month":
            since = now - timedelta(days=30)
        elif period == "year":
            since = now - timedelta(days=365)
        else:
            since = now - timedelta(weeks=1)
        
        # TODO: Implement proper trending algorithm
        # For now, just return most downloaded in period
        result = await self.db.execute(
            select(Lobster)
            .where(
                Lobster.is_deleted == False,
                Lobster.is_public == True,
                Lobster.updated_at >= since,
            )
            .order_by(desc(Lobster.download_count))
            .limit(limit)
        )
        items = result.scalars().all()
        
        return {
            "period": period,
            "items": list(items),
        }
    
    async def get_popular_tags(self, limit: int = 20) -> List[dict]:
        """获取热门标签"""
        # TODO: Implement tag aggregation
        # For now, return empty list
        return []
