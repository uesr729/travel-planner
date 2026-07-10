# ============================================================
# Dockerfile — AI 旅行规划师
# 适配 Railway 部署，支持动态 PORT 注入
# ============================================================
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录（SQLite 用）
RUN mkdir -p instance

# 接受 Railway 注入的 PORT，默认 5000
ARG PORT=5000
ENV PORT=${PORT}

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD exec gunicorn run:app --bind 0.0.0.0:${PORT} --workers 4 --timeout 120 --access-logfile - --error-logfile -
