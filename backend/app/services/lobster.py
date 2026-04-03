"""
Lobster Service
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lobster import Lobster, LobsterVersion, Star
from app.schemas.lobster import LobsterCreate, LobsterUpdate


class LobsterService:
    """Lobster 服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, lobster_id: UUID) -> Optional[Lobster]:
        """通过 ID 获取"""
        result = await self.db.execute(
            select(Lobster).where(Lobster.id == lobster_id, Lobster.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_full_name(self, namespace: str, name: str) -> Optional[Lobster]:
        """通过完整名称获取"""
        result = await self.db.execute(
            select(Lobster).where(
                Lobster.namespace == namespace,
                Lobster.name == name,
                Lobster.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()
    
    async def list_lobsters(
        self,
        namespace: Optional[str] = None,
        tag: Optional[str] = None,
        sort: str = "updated_at",
        order: str = "desc",
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[UUID] = None,
    ) -> dict:
        """获取列表"""
        query = select(Lobster).where(Lobster.is_deleted == False)
        
        # Filter by visibility
        if user_id:
            query = query.where(
                (Lobster.is_public == True) | (Lobster.owner_id == user_id)
            )
        else:
            query = query.where(Lobster.is_public == True)
        
        # Filter by namespace
        if namespace:
            query = query.where(Lobster.namespace == namespace)
        
        # Filter by tag
        if tag:
            query = query.where(Lobster.tags.contains([tag]))
        
        # Sort
        sort_field = getattr(Lobster, sort, Lobster.updated_at)
        if order == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # Pagination
        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return {
            "total": total,
            "items": list(items),
            "page": page,
            "page_size": page_size,
        }
    
    async def create(self, lobster_in: LobsterCreate, owner_id: UUID) -> Lobster:
        """创建 Lobster"""
        lobster = Lobster(
            name=lobster_in.name,
            namespace=lobster_in.namespace,
            description=lobster_in.description,
            readme=lobster_in.readme,
            is_public=lobster_in.is_public,
            tags=lobster_in.tags,
            owner_id=owner_id,
        )
        self.db.add(lobster)
        await self.db.commit()
        await self.db.refresh(lobster)
        return lobster
    
    async def update(self, lobster_id: UUID, lobster_in: LobsterUpdate) -> Optional[Lobster]:
        """更新 Lobster"""
        lobster = await self.get_by_id(lobster_id)
        if not lobster:
            return None
        
        update_data = lobster_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lobster, field, value)
        
        lobster.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(lobster)
        return lobster
    
    async def delete(self, lobster_id: UUID) -> bool:
        """删除 Lobster（软删除）"""
        lobster = await self.get_by_id(lobster_id)
        if not lobster:
            return False
        
        lobster.is_deleted = True
        lobster.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def get_versions(self, lobster_id: UUID) -> List[LobsterVersion]:
        """获取版本列表"""
        result = await self.db.execute(
            select(LobsterVersion)
            .where(LobsterVersion.lobster_id == lobster_id)
            .order_by(desc(LobsterVersion.created_at))
        )
        return list(result.scalars().all())
    
    async def create_version(
        self,
        lobster_id: UUID,
        version: str,
        description: Optional[str],
        file: UploadFile,
    ) -> dict:
        """创建新版本"""
        # TODO: Upload file to MinIO/S3
        file_url = f"s3://clawhub/{lobster_id}/{version}.clawpack"
        
        version_obj = LobsterVersion(
            lobster_id=lobster_id,
            version=version,
            description=description,
            file_url=file_url,
            file_size=0,  # TODO: Get file size
        )
        self.db.add(version_obj)
        
        # Update lobster
        lobster = await self.get_by_id(lobster_id)
        lobster.latest_version = version
        lobster.version_count += 1
        lobster.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(version_obj)
        
        return {
            "id": version_obj.id,
            "version": version_obj.version,
            "created_at": version_obj.created_at,
        }
    
    async def is_starred(self, lobster_id: UUID, user_id: UUID) -> bool:
        """检查是否已 star"""
        result = await self.db.execute(
            select(Star).where(
                Star.lobster_id == lobster_id,
                Star.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def toggle_star(self, lobster_id: UUID, user_id: UUID) -> bool:
        """切换 star 状态"""
        result = await self.db.execute(
            select(Star).where(
                Star.lobster_id == lobster_id,
                Star.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()
        
        lobster = await self.get_by_id(lobster_id)
        
        if existing:
            # Unstar
            await self.db.delete(existing)
            lobster.star_count -= 1
            await self.db.commit()
            return False
        else:
            # Star
            star = Star(lobster_id=lobster_id, user_id=user_id)
            self.db.add(star)
            lobster.star_count += 1
            await self.db.commit()
            return True
    
    async def get_by_owner(self, owner_id: UUID) -> List[Lobster]:
        """获取用户拥有的 Lobsters"""
        result = await self.db.execute(
            select(Lobster).where(
                Lobster.owner_id == owner_id,
                Lobster.is_deleted == False,
            )
        )
        return list(result.scalars().all())
    
    async def get_user_stars(self, user_id: UUID) -> List[Lobster]:
        """获取用户 star 的 Lobsters"""
        result = await self.db.execute(
            select(Lobster)
            .join(Star, Star.lobster_id == Lobster.id)
            .where(Star.user_id == user_id, Lobster.is_deleted == False)
        )
        return list(result.scalars().all())
    
    async def get_download_url(self, lobster_id: UUID, version: str) -> Optional[str]:
        """获取下载链接"""
        result = await self.db.execute(
            select(LobsterVersion).where(
                LobsterVersion.lobster_id == lobster_id,
                LobsterVersion.version == version,
            )
        )
        version_obj = result.scalar_one_or_none()
        return version_obj.file_url if version_obj else None
    
    async def increment_download(self, lobster_id: UUID, version: str) -> None:
        """增加下载计数"""
        lobster = await self.get_by_id(lobster_id)
        if lobster:
            lobster.download_count += 1
            await self.db.commit()
