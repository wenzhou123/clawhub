"""
ClawHub Lobster 模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import (
    String, Text, Integer, Boolean, ForeignKey, 
    UniqueConstraint, Index, func, Table, Column
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.version import Version
    from app.models.comment import Comment


class LobsterStatus(str, PyEnum):
    """Lobster 状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class LobsterVisibility(str, PyEnum):
    """Lobster 可见性枚举"""
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"  # 仅组织内可见


# Lobster-Tag 关联表
lobster_tag = Table(
    "lobster_tag",
    Base.metadata,
    Column("lobster_id", PGUUID(as_uuid=True), ForeignKey("lobster.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", PGUUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class Lobster(Base, SoftDeleteMixin, TimestampMixin):
    """Lobster 模型（Agent 配置包）"""
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Lobster 名称",
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="URL 友好的标识",
    )
    namespace: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="命名空间（用户名或组织名）",
    )
    full_name: Mapped[str] = mapped_column(
        String(201),
        unique=True,
        nullable=False,
        index=True,
        comment="完整名称（namespace/name）",
    )
    
    # 描述信息
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="简短描述",
    )
    readme: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="详细 README (Markdown)",
    )
    
    # 所有权
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # 状态和可见性
    status: Mapped[LobsterStatus] = mapped_column(
        default=LobsterStatus.DRAFT,
        nullable=False,
        index=True,
    )
    visibility: Mapped[LobsterVisibility] = mapped_column(
        default=LobsterVisibility.PUBLIC,
        nullable=False,
        index=True,
    )
    
    # 许可证信息
    license: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="SPDX 许可证标识",
    )
    license_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="许可证 URL",
    )
    
    # 元数据
    default_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="默认版本",
    )
    keywords: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="关键词列表",
    )
    
    # 统计信息
    stars_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        index=True,
    )
    downloads_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        index=True,
    )
    versions_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    comments_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    # 大小信息
    size_bytes: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="总大小（字节）",
    )
    
    # 关系
    owner: Mapped["User"] = relationship("User", back_populates="lobsters")
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="lobsters",
    )
    versions: Mapped[List["Version"]] = relationship(
        "Version",
        back_populates="lobster",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=lobster_tag,
        back_populates="lobsters",
    )
    stars: Mapped[List["Star"]] = relationship(
        "Star",
        back_populates="lobster",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    downloads: Mapped[List["Download"]] = relationship(
        "Download",
        back_populates="lobster",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    images: Mapped[List["LobsterImage"]] = relationship(
        "LobsterImage",
        back_populates="lobster",
        cascade="all, delete-orphan",
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="lobster",
        lazy="dynamic",
    )
    
    # 索引
    __table_args__ = (
        UniqueConstraint("namespace", "name", name="uq_lobster_namespace_name"),
        Index("idx_lobster_owner_status", "owner_id", "status"),
        Index("idx_lobster_org_status", "organization_id", "status"),
        Index("idx_lobster_stars", "stars_count"),
        Index("idx_lobster_downloads", "downloads_count"),
        Index("idx_lobster_search", "full_name"),
    )
    
    def __repr__(self) -> str:
        return f"<Lobster(full_name={self.full_name})>"
    
    @property
    def is_public(self) -> bool:
        """检查是否为公开"""
        return self.visibility == LobsterVisibility.PUBLIC
    
    @property
    def is_published(self) -> bool:
        """检查是否已发布"""
        return self.status == LobsterStatus.PUBLISHED
    
    def get_latest_version(self) -> Optional["Version"]:
        """获取最新版本"""
        return self.versions.filter(
            Version.is_deleted == False
        ).order_by(Version.created_at.desc()).first()


class Tag(Base):
    """标签模型"""
    
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        comment="十六进制颜色代码",
    )
    lobsters_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    # 关系
    lobsters: Mapped[List["Lobster"]] = relationship(
        "Lobster",
        secondary=lobster_tag,
        back_populates="tags",
    )
    
    def __repr__(self) -> str:
        return f"<Tag(name={self.name})>"


class Star(Base):
    """Star（收藏）模型"""
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="stars")
    lobster: Mapped["Lobster"] = relationship("Lobster", back_populates="stars")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint("user_id", "lobster_id", name="uq_star_user_lobster"),
    )
    
    def __repr__(self) -> str:
        return f"<Star(user={self.user_id}, lobster={self.lobster_id})>"


class Download(Base):
    """下载记录模型"""
    
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("version.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # 下载信息
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    downloaded_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )
    
    # 关系
    lobster: Mapped["Lobster"] = relationship("Lobster", back_populates="downloads")
    version: Mapped[Optional["Version"]] = relationship("Version", back_populates="downloads")
    
    # 索引
    __table_args__ = (
        Index("idx_download_lobster_at", "lobster_id", "downloaded_at"),
        Index("idx_download_user_at", "user_id", "downloaded_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Download(lobster={self.lobster_id}, version={self.version_id})>"


class LobsterImage(Base):
    """Lobster 截图/图片模型"""
    
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    caption: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    
    # 关系
    lobster: Mapped["Lobster"] = relationship("Lobster", back_populates="images")
    
    # 索引
    __table_args__ = (
        Index("idx_lobster_image_order", "lobster_id", "order"),
    )
    
    def __repr__(self) -> str:
        return f"<LobsterImage(lobster={self.lobster_id}, order={self.order})>"


class LobsterTag(Base):
    """Lobster-Tag 关联模型（显式定义用于类型提示）"""
    __tablename__ = "lobster_tag"
    
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    )
