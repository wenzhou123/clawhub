"""
ClawHub 数据库基础模块
定义所有模型的基类
"""
from datetime import datetime
from typing import Any
from uuid import uuid4, UUID

from sqlalchemy import DateTime, func, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明式基类
    
    所有模型都继承自此类，自动获得：
    - 表名自动转换（驼峰转下划线）
    - 通用字段（id, created_at, updated_at）
    - 序列化和字典转换方法
    """
    
    # 类型注解映射
    type_annotation_map = {
        datetime: DateTime(timezone=True),
        UUID: PGUUID(as_uuid=True),
    }
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动将类名转换为表名（驼峰转下划线）"""
        name = cls.__name__
        # 处理连续大写的情况（如 HTTPSProxy -> https_proxy）
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                # 如果前一个是小写，或者后一个是小写（不是连续大写）
                if name[i-1].islower() or (i + 1 < len(name) and name[i+1].islower()):
                    result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    # 通用主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    def __repr__(self) -> str:
        """对象的字符串表示"""
        attrs = []
        for key in ['id', 'name', 'username', 'email']:
            if hasattr(self, key):
                value = getattr(self, key)
                attrs.append(f"{key}={value}")
                break
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"
    
    def to_dict(self, exclude: set = None, include: set = None) -> dict:
        """
        将模型转换为字典
        
        Args:
            exclude: 要排除的字段集合
            include: 要包含的字段集合（优先于 exclude）
        
        Returns:
            模型数据的字典表示
        """
        result = {}
        exclude = exclude or set()
        
        for column in self.__table__.columns:
            key = column.name
            
            if include and key not in include:
                continue
            if not include and key in exclude:
                continue
            
            value = getattr(self, key)
            
            # 处理特殊类型
            if isinstance(value, UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            
            result[key] = value
        
        return result
    
    def update(self, **kwargs: Any) -> "Base":
        """
        批量更新字段
        
        Args:
            **kwargs: 要更新的字段和值
        
        Returns:
            self 支持链式调用
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class SoftDeleteMixin:
    """软删除混入类"""
    
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
    )
    
    def soft_delete(self) -> None:
        """执行软删除"""
        self.is_deleted = True
        self.deleted_at = func.now()
    
    def restore(self) -> None:
        """恢复软删除的实体"""
        self.is_deleted = False
        self.deleted_at = None


class TimestampMixin:
    """额外时间戳混入类（用于需要更多时间信息的模型）"""
    
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    
    archived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# 事件监听：自动更新 updated_at
@event.listens_for(Base, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """在更新前自动设置 updated_at"""
    target.updated_at = func.now()
