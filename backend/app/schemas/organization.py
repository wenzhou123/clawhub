"""
ClawHub 组织相关 Schema
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.models.organization import OrganizationRole, OrganizationStatus
from app.schemas.base import BaseSchema, TimestampIDSchema, PaginatedResponse


class OrganizationBase(BaseSchema):
    """组织基础 Schema"""
    
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    email: Optional[str] = Field(default=None, max_length=255)
    website: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=100)


class OrganizationCreate(OrganizationBase):
    """组织创建 Schema"""
    pass


class OrganizationUpdate(BaseSchema):
    """组织更新 Schema"""
    
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    email: Optional[str] = Field(default=None, max_length=255)
    website: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    banner_url: Optional[str] = Field(default=None, max_length=500)
    settings: Optional[dict] = None


class OrganizationResponse(TimestampIDSchema, OrganizationBase):
    """组织响应 Schema"""
    
    status: OrganizationStatus
    is_verified: bool
    avatar_url: Optional[str]
    banner_url: Optional[str]
    members_count: int
    lobsters_count: int
    stars_received: int
    settings: dict


class OrganizationDetail(OrganizationResponse):
    """组织详情 Schema"""
    
    max_members: int
    max_lobsters: int


class OrganizationPublic(BaseSchema):
    """组织公开信息 Schema"""
    
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    avatar_url: Optional[str]
    website: Optional[str]
    is_verified: bool
    members_count: int
    lobsters_count: int
    stars_received: int


# 组织成员 Schemas
class OrganizationMemberBase(BaseSchema):
    """组织成员基础 Schema"""
    
    role: OrganizationRole


class OrganizationMemberCreate(OrganizationMemberBase):
    """组织成员创建 Schema"""
    
    user_id: UUID


class OrganizationMemberUpdate(BaseSchema):
    """组织成员更新 Schema"""
    
    role: OrganizationRole
    permissions: Optional[dict] = None


class OrganizationMemberResponse(TimestampIDSchema):
    """组织成员响应 Schema"""
    
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    permissions: dict
    joined_at: Optional[datetime]
    user: dict  # 简化用户信息

    @field_validator("user", mode="before")
    @classmethod
    def format_user(cls, v):
        """格式化用户信息"""
        if hasattr(v, "__dict__"):
            return {
                "id": str(v.id),
                "username": v.username,
                "display_name": v.display_name or v.username,
                "avatar_url": v.avatar_url,
            }
        return v


class OrganizationMemberListItem(BaseSchema):
    """组织成员列表项 Schema"""
    
    id: UUID
    role: OrganizationRole
    joined_at: Optional[datetime]
    user: dict


class OrganizationMembersResponse(PaginatedResponse[OrganizationMemberListItem]):
    """组织成员列表响应 Schema"""
    pass


# 组织邀请
class OrganizationInviteRequest(BaseSchema):
    """组织邀请请求 Schema"""
    
    username_or_email: str = Field(..., min_length=1, max_length=255)
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationInviteResponse(BaseSchema):
    """组织邀请响应 Schema"""
    
    invite_id: UUID
    organization_id: UUID
    invited_user_id: UUID
    role: OrganizationRole
    invited_at: datetime


class OrganizationJoinRequest(BaseSchema):
    """加入组织请求 Schema"""
    
    invite_token: Optional[str] = None


class OrganizationLeaveRequest(BaseSchema):
    """离开组织请求 Schema"""
    
    transfer_owner_to: Optional[UUID] = None  # 如果是所有者离开，需要指定新所有者


# 组织列表
class OrganizationListResponse(PaginatedResponse[OrganizationPublic]):
    """组织列表响应 Schema"""
    pass


class OrganizationMemberSelfResponse(BaseSchema):
    """当前用户在组织中的成员信息 Schema"""
    
    organization_id: UUID
    role: OrganizationRole
    permissions: dict
    joined_at: Optional[datetime]
    is_owner: bool
    is_admin: bool
