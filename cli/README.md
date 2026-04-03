# ClawHub CLI

ClawHub 命令行工具，用于管理容器镜像和仓库。

## 安装

```bash
pip install clawhub-cli
```

或者从源码安装：

```bash
cd cli
pip install -e .
```

## 快速开始

### 1. 登录

```bash
clawhub login
# 或简写
ch login
```

### 2. 推送镜像

```bash
# 给镜像打标签并推送
clawhub push myapp:latest

# 推送到指定组织
clawhub push myorg/myapp:v1.0.0
```

### 3. 拉取镜像

```bash
clawhub pull myapp:latest
clawhub pull myorg/myapp:v1.0.0
```

### 4. 列出镜像

```bash
# 列出所有镜像
clawhub images

# 列出指定仓库的镜像
clawhub images -r myrepo
```

### 5. 管理仓库

```bash
# 列出仓库
clawhub repos

# 创建仓库
clawhub create-repo myrepo --public

# 删除仓库
clawhub delete myrepo
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `login` | 登录到 ClawHub |
| `logout` | 登出 ClawHub |
| `whoami` | 显示当前用户 |
| `pull` | 拉取镜像 |
| `push` | 推送镜像 |
| `images` | 列出镜像 |
| `repos` | 列出仓库 |
| `create-repo` | 创建仓库 |
| `delete` | 删除镜像或仓库 |
| `status` | 检查服务状态 |

## 配置

配置文件位于 `~/.clawhub/config.toml`：

```toml
[registry]
url = "https://clawhub.io"

[auth]
token = "your-token"

[defaults]
organization = "myorg"
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `CLAWHUB_REGISTRY` | Registry 地址 |
| `CLAWHUB_TOKEN` | 认证令牌 |
| `CLAWHUB_CONFIG` | 配置文件路径 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
ruff format .
mypy clawhub_cli/
```

## License

MIT
