"""
Lobsters API Endpoints
"""
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.lobster import (
    LobsterCreate,
    LobsterUpdate,
    LobsterResponse,
    LobsterDetailResponse,
    LobsterListResponse,
    LobsterVersionCreate,
)
from app.services.lobster import LobsterService
from app.services.user import UserService

router = APIRouter()


@router.get("", response_model=LobsterListResponse)
async def list_lobsters(
    namespace: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = Query("updated_at", regex="^(created_at|updated_at|stars|downloads|name)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """获取 Lobster 列表"""
    service = LobsterService(db)
    result = await service.list_lobsters(
        namespace=namespace,
        tag=tag,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
        user_id=current_user.id if current_user else None,
    )
    return result


@router.post("", response_model=LobsterResponse, status_code=status.HTTP_201_CREATED)
async def create_lobster(
    lobster_in: LobsterCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """创建新 Lobster"""
    service = LobsterService(db)
    
    # Use current user's username if namespace not provided
    if not lobster_in.namespace:
        lobster_in.namespace = current_user.username
    
    # Check if user has permission for the namespace
    if lobster_in.namespace != current_user.username:
        # TODO: Check organization membership
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create in this namespace",
        )
    
    # Check if lobster already exists
    existing = await service.get_by_full_name(lobster_in.namespace, lobster_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lobster {lobster_in.namespace}/{lobster_in.name} already exists",
        )
    
    lobster = await service.create(lobster_in, current_user.id)
    return lobster


@router.get("/{namespace}/{name}", response_model=LobsterDetailResponse)
async def get_lobster(
    namespace: str,
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """获取 Lobster 详情"""
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    # Check visibility
    if not lobster.is_public:
        if not current_user or lobster.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lobster not found",
            )
    
    # Get versions
    versions = await service.get_versions(lobster.id)
    lobster.versions = versions
    
    # Check if starred
    if current_user:
        lobster.is_starred = await service.is_starred(lobster.id, current_user.id)
    
    return lobster


@router.put("/{namespace}/{name}", response_model=LobsterResponse)
async def update_lobster(
    namespace: str,
    name: str,
    lobster_in: LobsterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """更新 Lobster"""
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    # Check ownership
    if lobster.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this lobster",
        )
    
    updated = await service.update(lobster.id, lobster_in)
    return updated


@router.delete("/{namespace}/{name}")
async def delete_lobster(
    namespace: str,
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """删除 Lobster"""
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    # Check ownership
    if lobster.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this lobster",
        )
    
    await service.delete(lobster.id)
    return {"message": "Lobster deleted successfully"}


@router.post("/{namespace}/{name}/versions", status_code=status.HTTP_201_CREATED)
async def create_version(
    namespace: str,
    name: str,
    version: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """上传新版本"""
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    # Check ownership
    if lobster.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this lobster",
        )
    
    version_data = await service.create_version(
        lobster_id=lobster.id,
        version=version,
        description=description,
        file=file,
    )
    
    return version_data


@router.post("/{namespace}/{name}/star")
async def star_lobster(
    namespace: str,
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """Star / Unstar Lobster"""
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    is_starred = await service.toggle_star(lobster.id, current_user.id)
    return {"starred": is_starred}


@router.get("/{namespace}/{name}/download/{version}")
async def download_version(
    namespace: str,
    name: str,
    version: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """下载 Lobster 版本"""
    from fastapi.responses import RedirectResponse
    
    service = LobsterService(db)
    lobster = await service.get_by_full_name(namespace, name)
    
    if not lobster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobster not found",
        )
    
    # Check visibility
    if not lobster.is_public:
        if not current_user or lobster.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lobster not found",
            )
    
    # Get download URL
    download_url = await service.get_download_url(lobster.id, version)
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )
    
    # Increment download count
    await service.increment_download(lobster.id, version)
    
    return RedirectResponse(url=download_url)
