"""
ClawHub 用户模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.organization import Organization, OrganizationMember
    from app.models.lobster import Lobster, Star
    from app.models.comment import Comment


class UserRole(str, PyEnum):
    """用户角色枚举"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    VERIFIED = "verified"
    USER = "user"
    GUEST = "guest"


class UserStatus(str, PyEnum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base, SoftDeleteMixin):
    """用户模型"""
    
    # 基本信息
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="用户名",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="邮箱",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希",
    )
    
    # 个人资料
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="显示名称",
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="个人简介",
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="头像 URL",
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="个人网站",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="所在地",
    )
    company: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="公司",
    )
    
    # 状态和角色
    role: Mapped[UserRole] = mapped_column(
        default=UserRole.USER,
        nullable=False,
        index=True,
        comment="用户角色",
    )
    status: Mapped[UserStatus] = mapped_column(
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
        index=True,
        comment="用户状态",
    )
    email_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="邮箱是否已验证",
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否为超级管理员",
    )
    
    # 安全相关
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间",
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="最后登录 IP",
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="登录失败次数",
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="账户锁定截止时间",
    )
    
    # 统计信息
    lobsters_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="创建的 Lobster 数量",
    )
    stars_received: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="收到的 Star 数量",
    )
    followers_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="粉丝数",
    )
    following_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="关注数",
    )
    
    # 偏好设置
    preferences: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="用户偏好设置",
    )
    
    # 关系
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    organizations: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lobsters: Mapped[List["Lobster"]] = relationship(
        "Lobster",
        back_populates="owner",
        lazy="dynamic",
    )
    stars: Mapped[List["Star"]] = relationship(
        "Star",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        lazy="dynamic",
    )
    
    # 关注关系
    following: Mapped[List["UserFollow"]] = relationship(
        "UserFollow",
        foreign_keys="UserFollow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers: Mapped[List["UserFollow"]] = relationship(
        "UserFollow",
        foreign_keys="UserFollow.following_id",
        back_populates="following_user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"
    
    @property
    def is_active(self) -> bool:
        """检查用户是否活跃"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @property
    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.locked_until:
            return datetime.now() < self.locked_until
        return False
    
    def increment_login_failure(self) -> None:
        """增加登录失败计数"""
        self.failed_login_attempts += 1
    
    def reset_login_failure(self) -> None:
        """重置登录失败计数"""
        self.failed_login_attempts = 0
    
    def record_login(self, ip: str) -> None:
        """记录登录信息"""
        self.last_login_at = datetime.now()
        self.last_login_ip = ip
        self.reset_login_failure()


class APIKey(Base, SoftDeleteMixin):
    """API Key 模型"""
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="API Key 名称",
    )
    key_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="API Key 哈希",
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后使用时间",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="过期时间",
    )
    scopes: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="权限范围",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="是否激活",
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    
    def __repr__(self) -> str:
        return f"<APIKey(name={self.name}, user={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """检查 API Key 是否过期"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


class UserFollow(Base):
    """用户关注关系模型"""
    
    follower_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    following_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 关系
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )
    following_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_user_follow"),
        Index("idx_user_follow_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<UserFollow(follower={self.follower_id}, following={self.following_id})>"
