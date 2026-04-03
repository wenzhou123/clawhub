"""
Comment Schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CommentBase(BaseModel):
    """评论基础 Schema"""
    content: str = Field(..., min_length=1, max_length=5000, description="评论内容")
    parent_id: Optional[UUID] = Field(None, description="父评论ID")


class CommentCreate(CommentBase):
    """创建评论"""
    lobster_id: UUID
    version_id: Optional[UUID]


class CommentUpdate(BaseModel):
    """更新评论"""
    content: Optional[str] = None


class CommentReactionBase(BaseModel):
    """评论反应基础 Schema"""
    reaction: str = Field(..., description="反应类型: +1, -1, heart, laugh, surprised")


class CommentReactionCreate(CommentReactionBase):
    """创建评论反应"""
    comment_id: UUID


class CommentReactionResponse(CommentReactionBase):
    """评论反应响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    comment_id: UUID
    user_id: UUID
    created_at: datetime


class CommentResponse(CommentBase):
    """评论响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lobster_id: UUID
    user_id: UUID
    user_username: Optional[str] = None
    user_avatar: Optional[str] = None
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    reactions: dict = Field(default_factory=dict)
