#!/bin/bash
# ClawHub Docker 启动脚本

set -e

echo "🦞 ClawHub Docker 启动脚本"
echo "=========================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo ""
    echo "请选择以下方式安装 Docker:"
    echo "1. Docker Desktop (推荐): brew install --cask docker"
    echo "2. Colima (轻量级): brew install colima docker docker-compose"
    echo ""
    echo "安装完成后，请重新运行此脚本"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "⚠️  Docker 未运行"
    echo ""
    
    # 尝试启动 Colima（如果使用 Colima）
    if command -v colima &> /dev/null; then
        echo "正在启动 Colima..."
        colima start || {
            echo "❌ Colima 启动失败"
            echo "请尝试手动启动: colima start"
            exit 1
        }
    else
        echo "❌ Docker 守护进程未运行"
        echo "请启动 Docker Desktop 或运行: colima start"
        exit 1
    fi
fi

echo "✅ Docker 已就绪"

# 进入项目目录
cd "$(dirname "$0")"

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p scripts nginx

# 确保 init-db.sh 存在
if [ ! -f scripts/init-db.sh ]; then
    cat > scripts/init-db.sh << 'EOF'
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOSQL
EOF
    chmod +x scripts/init-db.sh
fi

echo "🚀 启动 ClawHub 服务..."
docker-compose pull
docker-compose up -d --build

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "🎉 ClawHub 启动完成!"
echo ""
echo "访问地址:"
echo "  🌐 Web UI:      http://localhost:5173"
echo "  📚 API Docs:    http://localhost:8000/api/v1/docs"
echo "  💾 MinIO:       http://localhost:9001 (admin/adminadmin)"
echo ""
echo "常用命令:"
echo "  查看日志:      docker-compose logs -f"
echo "  停止服务:      docker-compose down"
echo "  重启服务:      docker-compose restart"
echo ""
