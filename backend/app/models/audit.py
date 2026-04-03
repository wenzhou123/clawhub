"""
ClawHub 审计日志模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditAction(str, PyEnum):
    """审计动作枚举"""
    # 用户相关
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PASSWORD_CHANGED = "user.password_changed"
    USER_EMAIL_VERIFIED = "user.email_verified"
    
    # Lobster 相关
    LOBSTER_CREATED = "lobster.created"
    LOBSTER_UPDATED = "lobster.updated"
    LOBSTER_DELETED = "lobster.deleted"
    LOBSTER_PUBLISHED = "lobster.published"
    LOBSTER_ARCHIVED = "lobster.archived"
    
    # 版本相关
    VERSION_CREATED = "version.created"
    VERSION_PUBLISHED = "version.published"
    VERSION_YANKED = "version.yanked"
    VERSION_DOWNLOADED = "version.downloaded"
    
    # 组织相关
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_DELETED = "org.deleted"
    ORG_MEMBER_ADDED = "org.member_added"
    ORG_MEMBER_REMOVED = "org.member_removed"
    ORG_MEMBER_ROLE_CHANGED = "org.member_role_changed"
    
    # 评论相关
    COMMENT_CREATED = "comment.created"
    COMMENT_UPDATED = "comment.updated"
    COMMENT_DELETED = "comment.deleted"
    COMMENT_FLAGGED = "comment.flagged"
    
    # Star 相关
    STAR_ADDED = "star.added"
    STAR_REMOVED = "star.removed"
    
    # API Key 相关
    API_KEY_CREATED = "api_key.created"
    API_KEY_DELETED = "api_key.deleted"
    API_KEY_USED = "api_key.used"
    
    # Webhook 相关
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_UPDATED = "webhook.updated"
    WEBHOOK_DELETED = "webhook.deleted"
    WEBHOOK_TRIGGERED = "webhook.triggered"
    
    # 系统相关
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


class AuditLog(Base):
    """审计日志模型"""
    
    # 动作信息
    action: Mapped[AuditAction] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    
    # 执行者
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_type: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
        comment="用户类型: user, api_key, system",
    )
    
    # 目标对象
    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="目标类型: user, lobster, version, org, comment 等",
    )
    target_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    
    # 请求信息
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    request_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # 变更详情
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="操作描述",
    )
    before_values: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="变更前的值",
    )
    after_values: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="变更后的值",
    )
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="额外元数据",
    )
    
    # 状态
    is_success: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 索引
    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_target", "target_type", "target_id"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_request", "request_id"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, user={self.user_id}, target={self.target_type}:{self.target_id})>"
    
    @classmethod
    def create(
        cls,
        action: AuditAction,
        target_type: str,
        target_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        **kwargs
    ) -> "AuditLog":
        """便捷创建方法"""
        return cls(
            action=action,
            target_type=target_type,
            target_id=target_id,
            user_id=user_id,
            **kwargs
        )
