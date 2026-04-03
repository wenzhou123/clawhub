# ClawHub - OpenClaw Registry 项目规格文档

## 项目概述
ClawHub 是一个类似 Docker Hub 的平台，专门为 OpenClaw 用户提供"龙虾"（Agent）配置的打包、上传、分享和管理服务。

## 核心功能需求

### 1. 用户系统
- 用户注册/登录（支持 GitHub OAuth）
- 用户个人主页
- 用户关注/粉丝系统

### 2. Lobster（龙虾）包管理
- 创建 Lobster 包（包含 SOUL.md, AGENTS.md, IDENTITY.md）
- 版本控制（支持多版本发布）
- 标签系统（tags）
- 包描述和 README

### 3. 上传与下载
- 命令行工具 `claw push/pull` 类似 docker
- Web 界面上传/下载
- 支持 .clawpack 格式打包文件

### 4. 发现与搜索
- 分类浏览（Engineering, Design, Marketing 等）
- 全文搜索
- 热门/趋势排行榜
- 评分和评论系统

### 5. 组织与团队
- 组织账户
- 团队协作
- 私有/公开包权限控制

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - Web 框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话
- **MinIO / S3** - 对象存储（存储包文件）
- **Celery** - 异步任务队列
- **SQLAlchemy 2.0** - ORM
- **Alembic** - 数据库迁移
- **JWT** - 认证

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由
- **Element Plus** / **Ant Design Vue** - UI 组件库
- **Axios** - HTTP 客户端

### CLI 工具
- **Python Click** - CLI 框架
- 支持 `claw login`, `claw push`, `claw pull`, `claw search`

## 数据库 Schema 概览

### 核心表
- `users` - 用户表
- `lobsters` - 龙虾包表
- `versions` - 版本表
- `organizations` - 组织表
- `tags` - 标签表
- `stars` - 收藏/点赞表
- `downloads` - 下载统计表
- `comments` - 评论表

## API 设计

### RESTful API
- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/auth/register` - 注册
- `GET /api/v1/lobsters` - 列表
- `POST /api/v1/lobsters` - 创建
- `GET /api/v1/lobsters/{namespace}/{name}` - 详情
- `POST /api/v1/lobsters/{id}/versions` - 发布版本
- `GET /api/v1/search?q=keyword` - 搜索

## 项目结构

```
clawhub/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # Pinia 状态
│   │   ├── api/            # API 封装
│   │   └── main.ts         # 入口
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── cli/                    # Python CLI 工具
│   ├── claw/
│   │   ├── commands/       # 命令实现
│   │   └── main.py         # 入口
│   ├── setup.py
│   └── README.md
├── docker-compose.yml      # 开发环境编排
└── README.md
```

## 开发阶段

### Phase 1: 基础架构
- [ ] 项目脚手架搭建
- [ ] 数据库设计和迁移
- [ ] 用户认证系统
- [ ] 基础 API 框架

### Phase 2: 核心功能
- [ ] Lobster 包 CRUD
- [ ] 版本管理
- [ ] 文件上传/下载
- [ ] 搜索功能

### Phase 3: 前端开发
- [ ] 基础布局和路由
- [ ] 用户相关页面
- [ ] Lobster 浏览/详情页
- [ ] 上传/发布流程

### Phase 4: CLI 工具
- [ ] CLI 框架搭建
- [ ] login/logout 命令
- [ ] push/pull 命令
- [ ] search 命令

### Phase 5: 完善功能
- [ ] 评论系统
- [ ] 组织功能
- [ ] 统计和排行榜
- [ ] 文档和示例

## 非功能性需求
- 支持高并发下载
- 包文件去重存储
- 完整的错误处理和日志
- API 限流保护
- 单元测试覆盖率 > 80%
