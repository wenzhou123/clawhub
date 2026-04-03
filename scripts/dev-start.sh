#!/bin/bash
# =====================================================
# ClawHub 开发环境启动脚本
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 帮助信息
show_help() {
    cat << EOF
ClawHub 开发环境管理脚本

用法: $0 [命令] [选项]

命令:
    start       启动开发环境（默认）
    stop        停止所有服务
    restart     重启所有服务
    build       重新构建镜像
    logs        查看日志
    shell       进入后端容器 shell
    db          进入数据库 shell
    redis       进入 Redis CLI
    minio       进入 MinIO 控制台
    clean       清理数据卷和容器
    status      查看服务状态
    test        运行测试
    migrate     运行数据库迁移
    seed        填充测试数据

选项:
    -h, --help  显示帮助信息
    -d          后台运行
    -f          强制重新构建

示例:
    $0 start           # 前台启动
    $0 start -d        # 后台启动
    $0 logs backend    # 查看后端日志
    $0 shell           # 进入后端容器
EOF
}

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    local deps=("docker" "docker-compose")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep 未安装，请先安装 Docker 和 Docker Compose"
            exit 1
        fi
    done
}

# 检查环境文件
check_env() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            log_warn ".env 文件不存在，从 .env.example 复制"
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_info "请编辑 .env 文件配置环境变量"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
}

# 启动服务
start_services() {
    local detached=""
    local force_build=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d) detached="-d"; shift ;;
            -f) force_build="--build"; shift ;;
            *) shift ;;
        esac
    done
    
    log_info "启动 ClawHub 开发环境..."
    
    cd "$PROJECT_ROOT"
    
    # 创建网络（如果不存在）
    docker network inspect clawhub-network >/dev/null 2>&1 || \
        docker network create clawhub-network
    
    if [ -n "$force_build" ]; then
        log_info "重新构建镜像..."
        docker-compose build --no-cache
    fi
    
    docker-compose up $detached
    
    if [ -z "$detached" ]; then
        log_info "服务已启动，按 Ctrl+C 停止"
    else
        log_success "服务已在后台启动"
        show_status
    fi
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    cd "$PROJECT_ROOT"
    docker-compose down
    log_success "所有服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    stop_services
    start_services "$@"
}

# 查看日志
show_logs() {
    cd "$PROJECT_ROOT"
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# 进入容器 shell
enter_shell() {
    local service="${1:-backend}"
    cd "$PROJECT_ROOT"
    docker-compose exec "$service" /bin/sh
}

# 进入数据库
enter_db() {
    cd "$PROJECT_ROOT"
    docker-compose exec postgres psql -U clawhub -d clawhub
}

# 进入 Redis
enter_redis() {
    cd "$PROJECT_ROOT"
    docker-compose exec redis redis-cli -a "${REDIS_PASSWORD:-clawhub_redis_secret}"
}

# 打开 MinIO 控制台
open_minio() {
    log_info "MinIO 控制台地址: http://localhost:9001"
    log_info "默认账号: clawhub / clawhub_minio_secret"
    
    # 尝试自动打开浏览器
    if command -v open &> /dev/null; then
        open "http://localhost:9001"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:9001"
    fi
}

# 清理环境
clean_environment() {
    log_warn "此操作将删除所有容器和数据卷！"
    read -p "是否继续? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT"
        docker-compose down -v
        docker system prune -f
        log_success "环境已清理"
    else
        log_info "操作已取消"
    fi
}

# 显示状态
show_status() {
    cd "$PROJECT_ROOT"
    echo ""
    echo "==============================================="
    echo "           ClawHub 服务状态"
    echo "==============================================="
    docker-compose ps
    echo ""
    echo "服务访问地址:"
    echo "  前端:      http://localhost:5173"
    echo "  后端 API:  http://localhost:8000"
    echo "  API 文档:  http://localhost:8000/docs"
    echo "  MinIO:     http://localhost:9001"
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis:     localhost:6379"
    echo "==============================================="
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    cd "$PROJECT_ROOT"
    docker-compose exec backend uv run pytest "$@"
}

# 数据库迁移
run_migrate() {
    log_info "运行数据库迁移..."
    cd "$PROJECT_ROOT"
    docker-compose exec backend uv run alembic upgrade head
}

# 填充测试数据
run_seed() {
    log_info "填充测试数据..."
    cd "$PROJECT_ROOT"
    docker-compose exec -e CLAWHUB_SEED_DATA=true postgres /docker-entrypoint-initdb.d/init-db.sh
}

# 主函数
main() {
    check_dependencies
    
    case "${1:-start}" in
        start)
            check_env
            shift
            start_services "$@"
            ;;
        stop)
            stop_services
            ;;
        restart)
            shift
            restart_services "$@"
            ;;
        build)
            cd "$PROJECT_ROOT"
            docker-compose build
            ;;
        logs)
            shift
            show_logs "$@"
            ;;
        shell)
            shift
            enter_shell "$@"
            ;;
        db)
            enter_db
            ;;
        redis)
            enter_redis
            ;;
        minio)
            open_minio
            ;;
        clean)
            clean_environment
            ;;
        status)
            show_status
            ;;
        test)
            shift
            run_tests "$@"
            ;;
        migrate)
            run_migrate
            ;;
        seed)
            run_seed
            ;;
        -h|--help|help)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
