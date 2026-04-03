# =====================================================
# ClawHub Frontend Dockerfile
# 基于 Node.js 20 + Vue 3 + Vite
# =====================================================

# -----------------------------------------------------
# 阶段 1: 依赖安装
# -----------------------------------------------------
FROM node:20-alpine AS dependencies

# 设置工作目录
WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 先复制包管理文件（利用 Docker 缓存层）
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# -----------------------------------------------------
# 阶段 2: 开发镜像
# -----------------------------------------------------
FROM node:20-alpine AS development

# 设置工作目录
WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 从依赖阶段复制 node_modules
COPY --from=dependencies /app/node_modules ./node_modules

# 复制项目文件
COPY . .

# 暴露开发服务器端口
EXPOSE 5173

# 开发服务器命令
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0"]

# -----------------------------------------------------
# 阶段 3: 构建生产版本
# -----------------------------------------------------
FROM dependencies AS builder

# 复制项目文件
COPY . .

# 构建生产版本
RUN npm run build

# -----------------------------------------------------
# 阶段 4: 生产镜像 (使用 Nginx)
# -----------------------------------------------------
FROM nginx:alpine AS production

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制生成的文件
COPY --from=builder /app/dist /usr/share/nginx/html

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

# -----------------------------------------------------
# 阶段 5: 静态文件服务器（用于测试）
# -----------------------------------------------------
FROM node:20-alpine AS preview

# 安装 serve
RUN npm install -g serve

# 设置工作目录
WORKDIR /app

# 从构建阶段复制生成的文件
COPY --from=builder /app/dist ./dist

# 暴露端口
EXPOSE 3000

# 启动静态服务器
CMD ["serve", "-s", "dist", "-l", "3000"]
