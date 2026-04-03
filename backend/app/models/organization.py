"""
ClawHub 组织模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lobster import Lobster


class OrganizationRole(str, PyEnum):
    """组织角色枚举"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrganizationStatus(str, PyEnum):
    """组织状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Organization(Base, SoftDeleteMixin):
    """组织模型"""
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="组织名称（唯一标识）",
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="组织显示名称",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="组织描述",
    )
    
    # 视觉元素
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="组织头像 URL",
    )
    banner_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="组织横幅 URL",
    )
    
    # 联系信息
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="组织邮箱",
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="组织网站",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="组织所在地",
    )
    
    # 状态和配置
    status: Mapped[OrganizationStatus] = mapped_column(
        default=OrganizationStatus.ACTIVE,
        nullable=False,
        index=True,
        comment="组织状态",
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否已认证",
    )
    settings: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="组织设置",
    )
    
    # 配额和限制
    max_members: Mapped[int] = mapped_column(
        default=50,
        nullable=False,
        comment="最大成员数",
    )
    max_lobsters: Mapped[int] = mapped_column(
        default=100,
        nullable=False,
        comment="最大 Lobster 数量",
    )
    
    # 统计信息
    members_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="成员数量",
    )
    lobsters_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Lobster 数量",
    )
    stars_received: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="收到的 Star 数量",
    )
    
    # 关系
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    lobsters: Mapped[List["Lobster"]] = relationship(
        "Lobster",
        back_populates="organization",
        lazy="dynamic",
    )
    
    def __repr__(self) -> str:
        return f"<Organization(name={self.name}, display_name={self.display_name})>"
    
    @property
    def is_active(self) -> bool:
        """检查组织是否活跃"""
        return self.status == OrganizationStatus.ACTIVE and not self.is_deleted
    
    def has_member(self, user_id: UUID) -> bool:
        """检查用户是否是成员"""
        return any(
            member.user_id == user_id and not member.is_deleted
            for member in self.members
        )
    
    def get_member(self, user_id: UUID) -> Optional["OrganizationMember"]:
        """获取成员信息"""
        for member in self.members:
            if member.user_id == user_id and not member.is_deleted:
                return member
        return None
    
    def can_add_member(self) -> bool:
        """检查是否可以添加成员"""
        return self.members_count < self.max_members


class OrganizationMember(Base, SoftDeleteMixin):
    """组织成员模型"""
    
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[OrganizationRole] = mapped_column(
        default=OrganizationRole.MEMBER,
        nullable=False,
        index=True,
        comment="成员角色",
    )
    
    # 权限覆盖
    permissions: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="特殊权限配置",
    )
    
    # 邀请信息
    invited_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="邀请人 ID",
    )
    invited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="邀请时间",
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="加入时间",
    )
    
    # 关系
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="organizations",
    )
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        Index("idx_org_member_role", "organization_id", "role"),
    )
    
    def __repr__(self) -> str:
        return f"<OrganizationMember(org={self.organization_id}, user={self.user_id}, role={self.role})>"
    
    @property
    def is_owner(self) -> bool:
        """检查是否为所有者"""
        return self.role == OrganizationRole.OWNER
    
    @property
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        return self.role in [OrganizationRole.OWNER, OrganizationRole.ADMIN]
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        # 所有者拥有所有权限
        if self.is_owner:
            return True
        
        # 检查特殊权限配置
        return self.permissions.get(permission, False)
