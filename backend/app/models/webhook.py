"""
ClawHub Webhook 模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.lobster import Lobster


class WebhookEvent(str, PyEnum):
    """Webhook 事件类型枚举"""
    # Lobster 事件
    LOBSTER_CREATED = "lobster.created"
    LOBSTER_UPDATED = "lobster.updated"
    LOBSTER_DELETED = "lobster.deleted"
    LOBSTER_PUBLISHED = "lobster.published"
    
    # 版本事件
    VERSION_CREATED = "version.created"
    VERSION_PUBLISHED = "version.published"
    VERSION_YANKED = "version.yanked"
    
    # Star 事件
    STAR_ADDED = "star.added"
    STAR_REMOVED = "star.removed"
    
    # 组织事件
    ORG_MEMBER_ADDED = "org.member_added"
    ORG_MEMBER_REMOVED = "org.member_removed"
    
    # 评论事件
    COMMENT_CREATED = "comment.created"


class WebhookStatus(str, PyEnum):
    """Webhook 状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"  # 因失败过多暂停


class Webhook(Base, SoftDeleteMixin):
    """Webhook 模型"""
    
    # 所有者
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Webhook 名称",
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="回调 URL",
    )
    secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="签名密钥",
    )
    
    # 事件配置
    events: Mapped[list] = mapped_column(
        ARRAY(String(50)),
        nullable=False,
        comment="订阅的事件列表",
    )
    
    # 状态
    status: Mapped[WebhookStatus] = mapped_column(
        default=WebhookStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    
    # 统计
    total_calls: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    successful_calls: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    failed_calls: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    
    # 失败处理
    consecutive_failures: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    max_retries: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
    )
    timeout_seconds: Mapped[int] = mapped_column(
        default=30,
        nullable=False,
    )
    
    # 请求头
    custom_headers: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    
    # 关系
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery",
        back_populates="webhook",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    
    # 索引
    __table_args__ = (
        Index("idx_webhook_owner_status", "owner_id", "status"),
        Index("idx_webhook_org_status", "organization_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Webhook(name={self.name}, url={self.url})>"
    
    def record_success(self) -> None:
        """记录成功调用"""
        self.total_calls += 1
        self.successful_calls += 1
        self.consecutive_failures = 0
        self.last_triggered_at = datetime.now()
        self.last_success_at = datetime.now()
    
    def record_failure(self) -> None:
        """记录失败调用"""
        self.total_calls += 1
        self.failed_calls += 1
        self.consecutive_failures += 1
        self.last_triggered_at = datetime.now()
        self.last_failure_at = datetime.now()
        
        # 连续失败过多则暂停
        if self.consecutive_failures >= 10:
            self.status = WebhookStatus.SUSPENDED
    
    def is_subscribed_to(self, event: str) -> bool:
        """检查是否订阅了指定事件"""
        return event in self.events or "*" in self.events


class WebhookDelivery(Base):
    """Webhook 投递记录模型"""
    
    webhook_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("webhook.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 事件信息
    event: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )
    
    # 请求信息
    request_headers: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
    )
    request_body: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    
    # 响应信息
    response_status: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    response_headers: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    response_body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 执行信息
    is_success: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="执行耗时（毫秒）",
    )
    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    # 关系
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="deliveries")
    
    # 索引
    __table_args__ = (
        Index("idx_webhook_delivery_webhook", "webhook_id", "created_at"),
        Index("idx_webhook_delivery_event", "event"),
    )
    
    def __repr__(self) -> str:
        return f"<WebhookDelivery(webhook={self.webhook_id}, event={self.event}, success={self.is_success})>"
