# ============================================================
# Dockerfile — 前端容器 (Nginx + 静态文件)
# 多阶段构建：第一阶段用 node 构建（当前项目无构建步骤），
# 第二阶段用 nginx:alpine 提供静态文件服务
# ============================================================
FROM nginx:alpine

# 将 Jinja2 模板和静态文件复制到 Nginx 目录
# 注意：由于本项目是 Flask 模板渲染，实际生产环境
# 需要后端渲染 HTML。这里 Nginx 只做反向代理 + 静态资源托管。
COPY travel_planner/static/ /usr/share/nginx/html/static/

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
