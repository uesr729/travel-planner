# ============================================================
# Dockerfile — 后端容器 (Flask + Gunicorn)
# Python 3.13-slim 基础镜像
# 数据库地址通过环境变量注入（服务名 "db"，非 localhost）
# ============================================================
FROM python:3.13-slim AS builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# 第二阶段：运行镜像（更小体积）
# ============================================================
FROM python:3.13-slim

WORKDIR /app

# 从 builder 阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目代码
COPY travel_planner/ travel_planner/
COPY config.py run.py Procfile ./

# 创建数据目录
RUN mkdir -p instance

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    PORT=8000

# 数据库地址必须使用服务名 "db"（由 docker-compose 注入）
# DATABASE_URL=postgresql://travel:travel123@db:5432/travel_planner

EXPOSE 8000

# 使用 gunicorn 启动，监听 0.0.0.0
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
