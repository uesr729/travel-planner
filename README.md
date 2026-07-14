# AI 旅行规划系统

## 项目简介

AI 旅行规划系统是一个基于 Flask 框架开发的智能旅行规划工具。用户输入目的地、天数、预算和偏好，系统即可自动生成包含景点、餐饮、住宿、费用概览和地图标注的完整行程规划。

**在线体验**：https://travel-planner-production-d9e9.up.railway.app

## 功能特性

- ✨ **一键生成** — 输入目的地和偏好，自动生成完整行程
- 🗺️ **地图展示** — Leaflet 地图标注所有景点，支持点击交互
- 💰 **费用概览** — 自动计算景点、餐饮、住宿等费用
- 🌤️ **天气信息** — 展示各日温度天气
- 🔗 **一键分享** — 生成唯一分享链接
- 📋 **历史记录** — 查看所有已生成的行程

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.13 + Flask 3.1 | Web 框架 |
| Flask-SQLAlchemy | 数据库 ORM |
| SQLite / PostgreSQL | 数据存储 |
| Jinja2 + Leaflet.js | 前端 + 地图 |
| Gunicorn | 生产部署 |
| 高德地图 API | 真实景点 POI 数据 |
| Railway | 云部署平台 |

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

浏览器打开 http://localhost:5000

### 环境变量配置

创建 `.env` 文件：

```env
AMAP_API_KEY=你的高德地图Web服务Key
FLASK_SECRET_KEY=你的密钥
```

## 项目结构

```
travel-planner/
├── run.py                     # 应用入口
├── config.py                  # 配置
├── requirements.txt           # Python 依赖
├── Procfile                   # 生产部署配置
├── travel_planner/
│   ├── __init__.py            # App 工厂
│   ├── models.py              # 数据模型
│   ├── routes/
│   │   └── main.py            # 路由定义
│   ├── services/
│   │   ├── llm_service.py     # LLM 行程生成
│   │   ├── mock_data.py       # Mock 数据
│   │   ├── weather.py         # 天气服务
│   │   └── poi_service.py     # 高德 POI 搜索
│   ├── templates/             # Jinja2 模板
│   └── static/                # CSS/JS
└── experiment6/               # 实验六产出
    ├── backend/Dockerfile
    ├── frontend/Dockerfile
    ├── frontend/nginx.conf
    ├── docker-compose.yml
    └── code-review-report.md
```

## 数据优先级

系统按以下优先级获取景点数据：

1. **高德 API** — 配置 Key 时获取真实景点
2. **内置数据** — 5 个核心城市预设景点
3. **通用生成** — 其他城市自动生成

## Docker 部署

```bash
docker compose -f experiment6/docker-compose.yml up -d
```

## 部署地址

- **线上**：https://travel-planner-production-d9e9.up.railway.app
- **仓库**：https://github.com/uesr729/travel-planner
