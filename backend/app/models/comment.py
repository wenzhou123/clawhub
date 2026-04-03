"""
ClawHub 评论模型
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Index, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lobster import Lobster


class CommentStatus(str, PyEnum):
    """评论状态枚举"""
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"
    FLAGGED = "flagged"


class Comment(Base, SoftDeleteMixin):
    """评论模型"""
    
    # 关联
    lobster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lobster.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="评论内容 (Markdown)",
    )
    content_html: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="渲染后的 HTML",
    )
    
    # 层级结构
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    depth: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="嵌套深度",
    )
    
    # 状态
    status: Mapped[CommentStatus] = mapped_column(
        default=CommentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    
    # 统计
    reactions_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    replies_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    # 编辑信息
    edited_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    edited_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 关系
    lobster: Mapped["Lobster"] = relationship("Lobster", back_populates="comments")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="comments")
    editor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[edited_by])
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side="Comment.id",
        back_populates="replies",
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        lazy="dynamic",
    )
    reactions: Mapped[List["CommentReaction"]] = relationship(
        "CommentReaction",
        back_populates="comment",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    
    # 索引
    __table_args__ = (
        Index("idx_comment_lobster_created", "lobster_id", "created_at"),
        Index("idx_comment_user_created", "user_id", "created_at"),
        Index("idx_comment_parent", "parent_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, lobster={self.lobster_id}, user={self.user_id})>"
    
    def edit(self, new_content: str, edited_by: UUID) -> None:
        """编辑评论"""
        self.content = new_content
        self.content_html = None  # 需要重新渲染
        self.edited_at = datetime.now()
        self.edited_by = edited_by
    
    def add_reply(self) -> None:
        """增加回复计数"""
        self.replies_count += 1


class CommentReaction(Base):
    """评论反应模型（点赞等）"""
    
    comment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="👍",
        comment="反应类型（emoji）",
    )
    
    # 关系
    comment: Mapped["Comment"] = relationship("Comment", back_populates="reactions")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "reaction_type", name="uq_comment_reaction"),
    )
    
    def __repr__(self) -> str:
        return f"<CommentReaction(comment={self.comment_id}, user={self.user_id}, type={self.reaction_type})>"
