"""
Users API Endpoints
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
) -> Any:
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """更新当前用户信息"""
    service = UserService(db)
    updated = await service.update(current_user.id, user_in)
    return updated


@router.get("/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取用户信息"""
    service = UserService(db)
    user = await service.get_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.get("/{username}/lobsters")
async def get_user_lobsters(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """获取用户的 Lobsters"""
    from app.services.lobster import LobsterService
    
    service = UserService(db)
    user = await service.get_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    lobster_service = LobsterService(db)
    lobsters = await lobster_service.get_by_owner(user.id)
    return {"items": lobsters}


@router.get("/{username}/stars")
async def get_user_stars(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """获取用户 Star 的 Lobsters"""
    from app.services.lobster import LobsterService
    
    service = UserService(db)
    user = await service.get_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if viewing own stars
    if not current_user or current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own stars",
        )
    
    lobster_service = LobsterService(db)
    stars = await lobster_service.get_user_stars(user.id)
    return {"items": stars}
