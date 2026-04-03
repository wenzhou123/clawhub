"""
ClawHub 数据库会话管理模块
提供同步和异步数据库会话管理
"""
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器单例类"""
    
    _instance: Optional["DatabaseManager"] = None
    _engine: Optional[Engine] = None
    _async_engine: Optional[AsyncEngine] = None
    _session_maker: Optional[sessionmaker] = None
    _async_session_maker: Optional[async_sessionmaker] = None
    
    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def init_engines(self) -> None:
        """初始化数据库引擎"""
        if self._engine is None:
            logger.info("Initializing sync database engine")
            self._engine = create_engine(
                str(settings.DATABASE_URL),
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.DEBUG,
            )
            self._session_maker = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
        
        if self._async_engine is None:
            logger.info("Initializing async database engine")
            self._async_engine = create_async_engine(
                str(settings.ASYNC_DATABASE_URL),
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.DEBUG,
            )
            self._async_session_maker = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
    
    @property
    def engine(self) -> Engine:
        """获取同步引擎"""
        if self._engine is None:
            self.init_engines()
        return self._engine
    
    @property
    def async_engine(self) -> AsyncEngine:
        """获取异步引擎"""
        if self._async_engine is None:
            self.init_engines()
        return self._async_engine
    
    @property
    def session_maker(self) -> sessionmaker:
        """获取同步会话工厂"""
        if self._session_maker is None:
            self.init_engines()
        return self._session_maker
    
    @property
    def async_session_maker(self) -> async_sessionmaker:
        """获取异步会话工厂"""
        if self._async_session_maker is None:
            self.init_engines()
        return self._async_session_maker
    
    def close(self) -> None:
        """关闭数据库引擎"""
        if self._engine:
            logger.info("Closing sync database engine")
            self._engine.dispose()
            self._engine = None
        if self._async_engine:
            logger.info("Closing async database engine")
            # 异步引擎关闭需要在异步上下文中进行
            self._async_engine = None
        self._session_maker = None
        self._async_session_maker = None
    
    async def close_async(self) -> None:
        """异步关闭数据库引擎"""
        if self._async_engine:
            logger.info("Closing async database engine")
            await self._async_engine.dispose()
            self._async_engine = None


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 同步会话管理
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    获取同步数据库会话（上下文管理器）
    
    Usage:
        with get_db_session() as session:
            result = session.query(User).first()
    """
    session = db_manager.session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    获取同步数据库会话（生成器，用于依赖注入）
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    with get_db_session() as session:
        yield session


# 异步会话管理
@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话（异步上下文管理器）
    
    Usage:
        async with get_async_db_session() as session:
            result = await session.execute(select(User))
    """
    session = db_manager.async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Async database session error: {e}")
        raise
    finally:
        await session.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话（异步生成器，用于依赖注入）
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with get_async_db_session() as session:
        yield session


# 事务管理
@contextmanager
def transaction(session: Session) -> Generator[Session, None, None]:
    """
    同步事务上下文管理器
    
    Usage:
        with get_db_session() as session:
            with transaction(session):
                session.add(user)
    """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


@asynccontextmanager
async def async_transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    异步事务上下文管理器
    
    Usage:
        async with get_async_db_session() as session:
            async with async_transaction(session):
                session.add(user)
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


# 数据库健康检查
def check_db_connection() -> bool:
    """检查同步数据库连接"""
    try:
        with get_db_session() as session:
            session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def check_async_db_connection() -> bool:
    """检查异步数据库连接"""
    try:
        async with get_async_db_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Async database connection check failed: {e}")
        return False
