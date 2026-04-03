#!/bin/bash
# =====================================================
# ClawHub 数据库初始化脚本
# 此脚本在 PostgreSQL 容器启动时自动执行
# =====================================================

set -e

echo "==============================================="
echo "Initializing ClawHub Database..."
echo "==============================================="

# 创建数据库用户（如果不存在）
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 创建扩展
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    
    -- 创建 schema
    CREATE SCHEMA IF NOT EXISTS clawhub;
    
    -- 设置搜索路径
    ALTER DATABASE $POSTGRES_DB SET search_path TO clawhub, public;
    
    -- 创建应用专用角色（可选，用于生产环境）
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'clawhub_app') THEN
            CREATE ROLE clawhub_app WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}_app';
        END IF;
    END
    \$\$;
    
    -- 授权
    GRANT ALL PRIVILEGES ON SCHEMA clawhub TO clawhub_app;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA clawhub TO clawhub_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA clawhub GRANT ALL ON TABLES TO clawhub_app;
    
    -- 创建触发函数：自动更新 updated_at 字段
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    \$\$ language 'plpgsql';
    
    -- 创建通知函数（用于实时更新）
    CREATE OR REPLACE FUNCTION notify_change()
    RETURNS TRIGGER AS \$\$
    BEGIN
        PERFORM pg_notify(
            'table_change',
            json_build_object(
                'table', TG_TABLE_NAME,
                'action', TG_OP,
                'data', row_to_json(NEW)
            )::text
        );
        RETURN NEW;
    END;
    \$\$ LANGUAGE plpgsql;
    
    COMMENT ON FUNCTION update_updated_at_column() IS '自动更新 updated_at 时间戳';
    COMMENT ON FUNCTION notify_change() IS '数据变更通知函数';
EOSQL

# 创建初始数据（可选）
if [ "$CLAWHUB_SEED_DATA" = "true" ]; then
    echo "Seeding initial data..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        -- 创建默认组织
        INSERT INTO clawhub.organizations (name, slug, description, is_active)
        VALUES ('Default', 'default', 'Default organization', true)
        ON CONFLICT (slug) DO NOTHING;
        
        -- 创建系统管理员用户（密码需要在应用中单独设置）
        INSERT INTO clawhub.users (username, email, is_superuser, is_active)
        VALUES ('admin', 'admin@clawhub.local', true, true)
        ON CONFLICT (email) DO NOTHING;
EOSQL
fi

echo "==============================================="
echo "Database initialization completed!"
echo "==============================================="
