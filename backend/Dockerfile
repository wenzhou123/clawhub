# =====================================================
# ClawHub Backend Dockerfile
# 基于 Python 3.11 + uv 包管理器
# =====================================================

# -----------------------------------------------------
# 阶段 1: 依赖安装
# -----------------------------------------------------
FROM python:3.11-slim AS dependencies

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖到虚拟环境
RUN uv sync --frozen --no-install-project

# -----------------------------------------------------
# 阶段 2: 生产镜像
# -----------------------------------------------------
FROM python:3.11-slim AS production

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r clawhub && useradd -r -g clawhub clawhub

# 设置工作目录
WORKDIR /app

# 从依赖阶段复制虚拟环境
COPY --from=dependencies /app/.venv /app/.venv

# 复制应用代码
COPY --chown=clawhub:clawhub app/ ./app/
COPY --chown=clawhub:clawhub alembic/ ./alembic/
COPY --chown=clawhub:clawhub alembic.ini ./

# 设置 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 切换到非 root 用户
USER clawhub

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------
# 阶段 3: 开发镜像
# -----------------------------------------------------
FROM dependencies AS development

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# 安装开发依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 设置工作目录
WORKDIR /app

# 设置 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 暴露端口
EXPOSE 8000

# 开发模式命令（热重载）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
