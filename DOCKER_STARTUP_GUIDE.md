# 🐳 ClawHub Docker 启动指南

## 方案一：使用 Docker Desktop（推荐）

### 1. 安装 Docker Desktop

```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或者手动下载安装
# 访问 https://www.docker.com/products/docker-desktop 下载
```

### 2. 启动 Docker Desktop
- 打开 Launchpad，点击 Docker 图标
- 等待 Docker Desktop 启动完成（菜单栏显示 🐳 图标）

### 3. 验证安装
```bash
docker --version
docker-compose --version
docker ps
```

### 4. 启动 ClawHub
```bash
cd /Users/wenzhou/Documents/Project/clawhub

# 复制环境变量文件
cp .env.example .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 方案二：使用 Colima（轻量级）

### 1. 安装 Colima 和 Docker CLI
```bash
brew install colima docker docker-compose
```

### 2. 启动 Colima
```bash
# 基本启动
colima start

# 或者指定配置
colima start --cpu 4 --memory 8 --disk 50

# 使用 QEMU 虚拟机（如果默认 VZ 有问题）
colima start --vm-type qemu

# 国内镜像加速（如网络问题）
colima start --dns 8.8.8.8
```

### 3. 验证
```bash
colima status
docker ps
```

### 4. 启动 ClawHub
```bash
cd /Users/wenzhou/Documents/Project/clawhub
docker-compose up -d
```

---

## 方案三：使用 Podman（RedHat 替代方案）

### 1. 安装 Podman
```bash
brew install podman podman-compose
```

### 2. 初始化并启动 Podman 机器
```bash
podman machine init --cpus 4 --memory 8192 --disk-size 50
podman machine start
```

### 3. 使用 Podman 启动
```bash
cd /Users/wenzhou/Documents/Project/clawhub
podman-compose up -d
```

---

## 方案四：手动本地开发（不使用 Docker）

### 1. 安装依赖
```bash
# 安装 PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 安装 Redis
brew install redis
brew services start redis

# 安装 MinIO (可选，也可使用 AWS S3)
brew install minio/stable/minio
```

### 2. 初始化数据库
```bash
createdb clawhub
```

### 3. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload
```

### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

---

## 启动后的访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Web UI | http://localhost:5173 | 前端界面 |
| API 文档 | http://localhost:8000/api/v1/docs | Swagger UI |
| API Redoc | http://localhost:8000/api/v1/redoc | ReDoc 文档 |
| MinIO | http://localhost:9001 | 对象存储控制台 |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存 |

---

## 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止所有服务
docker-compose down

# 停止并删除数据卷（清理所有数据）
docker-compose down -v

# 重建镜像
docker-compose build --no-cache

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U clawhub -d clawhub
```

---

## 故障排除

### 1. 端口冲突
如果端口被占用，修改 `.env` 文件中的端口配置：
```env
BACKEND_PORT=8001
FRONTEND_PORT=5174
POSTGRES_PORT=5433
```

### 2. 权限问题
```bash
# 修复 Docker 权限
sudo chown -R $(whoami) ~/.docker

# Colima 权限
colima stop
colima start --mount-type virtiofs
```

### 3. 网络问题（镜像下载失败）
```bash
# 配置 Docker 镜像加速
# 编辑 ~/.docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

### 4. Colima 启动失败
```bash
# 完全重置 Colima
colima stop
colima delete
rm -rf ~/.colima ~/.lima
colima start

# 或者使用 QEMU 替代 VZ
colima start --vm-type qemu
```

### 5. 数据库连接失败
```bash
# 等待数据库完全启动
docker-compose logs -f postgres

# 手动初始化数据库
docker-compose exec postgres psql -U clawhub -c "CREATE DATABASE clawhub;"
```

---

## 环境变量说明

关键配置项（在 `.env` 文件中）：

```env
# 数据库
POSTGRES_USER=clawhub
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=clawhub

# JWT 密钥（生产环境必须修改）
SECRET_KEY=your_super_secret_key

# MinIO
MINIO_ROOT_USER=clawhub
MINIO_ROOT_PASSWORD=your_minio_password

# CORS（前端地址）
CORS_ORIGINS=http://localhost:5173
```

---

## 生产部署

生产环境建议使用：
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

生产配置包含：
- Nginx 反向代理
- SSL/TLS 支持
- 更严格的资源限制
- 日志收集

---

## 需要帮助？

1. 查看项目 README: `/Users/wenzhou/Documents/Project/clawhub/README.md`
2. 检查服务日志: `docker-compose logs -f`
3. 提交 Issue 到项目仓库
