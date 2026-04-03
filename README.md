# 🦞 ClawHub

> OpenClaw 的容器注册中心 - 发现、分享和分发你的 AI Agent 配置

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Vue](https://img.shields.io/badge/vue-3.0-green)

## 项目简介

ClawHub 是一个类似 Docker Hub 的平台，专门为 [OpenClaw](https://github.com/openclaw/openclaw) 用户提供"龙虾"（Lobster）配置的打包、上传、分享和管理服务。

用户可以将包含 `SOUL.md`, `AGENTS.md`, `IDENTITY.md` 的 OpenClaw 配置打包成 `.clawpack` 文件，上传到 ClawHub 与他人分享。

## 核心功能

- 🔐 **用户系统** - 注册/登录，支持 GitHub OAuth
- 📦 **Lobster 管理** - 创建、版本控制、标签管理
- ⬆️ **上传下载** - Web 界面和 CLI 工具双重支持
- 🔍 **发现搜索** - 分类浏览、全文搜索、热门排行
- 👥 **组织团队** - 组织账户，团队协作
- 🖥️ **CLI 工具** - `claw push/pull/search` 类似 docker 命令

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - 高性能 Web 框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话
- **MinIO** - 对象存储
- **SQLAlchemy 2.0** - ORM

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **Element Plus** - UI 组件库

### CLI
- **Python Click** - CLI 框架
- **Rich** - 美观的终端输出

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.11+ (开发)
- Node.js 20+ (开发)

### 使用 Docker Compose 启动

```bash
# 克隆项目
git clone <repository>
 cd clawhub

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：
- Web UI: http://localhost:5173
- API Docs: http://localhost:8000/api/v1/docs
- MinIO Console: http://localhost:9001

### CLI 安装

```bash
cd cli
pip install -e .

# 登录
claw login

# 初始化 Lobster
claw init my-lobster

# 推送
cd my-lobster
claw push . -v 1.0.0

# 拉取
claw pull username/lobster-name:1.0.0
```

## 项目结构

```
clawhub/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口
│   ├── alembic/            # 数据库迁移
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # Pinia 状态
│   │   └── api/            # API 封装
│   └── package.json
├── cli/                    # Python CLI 工具
│   └── claw/
├── docker-compose.yml      # 开发环境
└── README.md
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 开发

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 配置

### 环境变量

创建 `.env` 文件：

```env
# 数据库
POSTGRES_USER=clawhub
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=clawhub

# JWT
SECRET_KEY=your_super_secret_key

# MinIO
MINIO_ROOT_USER=clawhub
MINIO_ROOT_PASSWORD=your_minio_password
```

## CLI 命令

| 命令 | 描述 |
|------|------|
| `claw login` | 登录到 ClawHub |
| `claw logout` | 登出 |
| `claw whoami` | 显示当前用户 |
| `claw init <name>` | 初始化 Lobster 目录 |
| `claw push <path>` | 打包并上传 |
| `claw pull <ref>` | 下载 Lobster |
| `claw search <keyword>` | 搜索 |
| `claw list` | 列出我的 Lobsters |

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License

---

Made with ❤️ for the OpenClaw community
