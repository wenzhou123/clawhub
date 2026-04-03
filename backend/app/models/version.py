"""
ClawHub Lobster 版本模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.lobster import Lobster
    from app.models.comment import Comment


class VersionStatus(str, PyEnum):
    """版本状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    YANKED = "yanked"  # 已撤回，不推荐使用的版本


class Version(Base, SoftDeleteMixin):
    """Lobster 版本模型"""
    
    # 关联
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 版本信息
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="版本号（遵循语义化版本）",
    )
    revision: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
        comment="修订号（同一版本的多次上传）",
    )
    
    # 描述
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="版本描述",
    )
    changelog: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="变更日志 (Markdown)",
    )
    
    # 状态
    status: Mapped[VersionStatus] = mapped_column(
        default=VersionStatus.DRAFT,
        nullable=False,
        index=True,
    )
    is_latest: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="是否为最新版本",
    )
    
    # 文件信息
    file_size: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="文件大小（字节）",
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="文件 SHA256 哈希",
    )
    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="文件存储路径/URL",
    )
    
    # 配置内容（可选，小文件可直接存储）
    config_content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="解析后的配置内容",
    )
    
    # 元数据
    extra_metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="额外元数据",
    )
    
    # 统计
    downloads_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    # 发布信息
    published_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        index=True,
    )
    published_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # yank 信息
    yanked_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    yanked_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 关系
    lobster: Mapped["Lobster"] = relationship("Lobster", back_populates="versions")
    downloads: Mapped[List["Download"]] = relationship(
        "Download",
        back_populates="version",
        lazy="dynamic",
    )
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint("lobster_id", "version", "revision", name="uq_version_lobster_ver_rev"),
        Index("idx_version_lobster_latest", "lobster_id", "is_latest"),
        Index("idx_version_published", "published_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Version(lobster={self.lobster_id}, version={self.version}, revision={self.revision})>"
    
    @property
    def full_version(self) -> str:
        """获取完整版本号（含修订号）"""
        if self.revision > 1:
            return f"{self.version}-{self.revision}"
        return self.version
    
    @property
    def is_available(self) -> bool:
        """检查版本是否可用（未撤回且未删除）"""
        return self.status not in [VersionStatus.YANKED] and not self.is_deleted
    
    def get_download_url(self) -> str:
        """获取下载 URL"""
        # 这里应该返回预签名 URL 或公开 URL
        return f"/api/v1/versions/{self.id}/download"


class VersionDependency(Base):
    """版本依赖模型"""
    
    version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("version.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 依赖信息
    dependency_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="依赖类型: lobster, python, system",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="依赖名称",
    )
    version_constraint: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="版本约束",
    )
    is_optional: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否为可选依赖",
    )
    
    def __repr__(self) -> str:
        return f"<VersionDependency(version={self.version_id}, name={self.name})>"
