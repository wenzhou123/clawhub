"""
ClawHub 配置管理模块
"""
from functools import lru_cache
from typing import Any, List, Optional, Union
from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # 应用基础配置
    PROJECT_NAME: str = "ClawHub"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "OpenClaw Agent 配置分享平台"
    DEBUG: bool = False
    
    # API 配置
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "clawhub"
    POSTGRES_PASSWORD: str = "clawhub_secret"
    POSTGRES_DB: str = "clawhub"
    DATABASE_URL: Optional[PostgresDsn] = None
    ASYNC_DATABASE_URL: Optional[PostgresDsn] = None
    
    # 连接池配置
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        """组装同步数据库连接 URL"""
        if isinstance(v, str):
            return v
        
        data = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_SERVER"),
            port=data.get("POSTGRES_PORT"),
            path=data.get("POSTGRES_DB", ""),
        )
    
    @field_validator("ASYNC_DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: Optional[str], info) -> Any:
        """组装异步数据库连接 URL"""
        if isinstance(v, str):
            return v
        
        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_SERVER"),
            port=data.get("POSTGRES_PORT"),
            path=data.get("POSTGRES_DB", ""),
        )
    
    # Redis 配置
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT 配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MinIO/S3 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "clawhub"
    MINIO_SECURE: bool = False
    MINIO_REGION: str = "us-east-1"
    
    # 存储配置
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".zip", ".tar.gz", ".tgz"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 秒
    
    # 缓存配置 (秒)
    CACHE_TTL_USER: int = 300
    CACHE_TTL_LOBSTER: int = 60
    CACHE_TTL_VERSION: int = 300
    CACHE_TTL_LIST: int = 30
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """解析 CORS 来源列表"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 组织配置
    MAX_ORGANIZATIONS_PER_USER: int = 5
    MAX_MEMBERS_PER_ORGANIZATION: int = 50
    
    # Lobster 配置
    MAX_TAGS_PER_LOBSTER: int = 10
    MAX_LOBSTERS_PER_USER: int = 100
    MAX_VERSIONS_PER_LOBSTER: int = 50
    
    # 搜索配置
    SEARCH_MIN_CHARS: int = 2
    SEARCH_MAX_RESULTS: int = 100


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
