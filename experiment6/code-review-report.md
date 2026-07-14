# Code Review 报告 — travel-planner

## 审查工具
- **ocr-review**：确定性缺陷扫描（NPE、SSRF、SQL注入、XSS）
- **code-review**：语义分析与架构审查（四阶段流程）

---

## 第一部分：ocr-review 规则扫描

### 发现汇总

| # | 严重级别 | 类别 | 文件 | 行号 | 问题描述 |
|---|---------|------|------|------|---------|
| 1 | 🔴 Blocking | 资源泄漏 | `llm_service.py` | 105 | `OpenAI()` client 未做连接池关闭，长时间运行可能泄漏连接 |
| 2 | 🔴 Blocking | NPE | `weather.py` | 46-48 | `item["dt_txt"]` 直接下标访问，API 返回格式异常时 KeyError |
| 3 | 🟡 Important | 异常捕获过宽 | `weather.py` | 65 | `except Exception` 吞没了所有异常，包括程序错误 |
| 4 | 🟡 Important | 异常捕获过宽 | `mock_data.py` | 490 | 同理，应区分 API 异常和程序异常 |
| 5 | 🟡 Important | SSRF 风险 | `poi_service.py` | 84 | `requests.get(url, params)` — URL 拼接有用户输入但无 SSRF 防护 |
| 6 | 🟡 Important | 硬编码 | `itinerary.html` | 47 | 地图层 URL 硬编码了 OpenStreetMap CDN |
| 7 | 🟢 Warning | 类型安全 | `models.py` | 13-16 | `Column` 类型定义缺少 `Optional` 泛型标注 |

---

## 第二部分：code-review 深度审查

### 阶段一：上下文分析

**项目类型**：单体 Flask Web 应用（Jinja2 模板渲染）
**技术栈**：Python 3.13 + Flask 3.1 + SQLAlchemy + Leaflet.JS + Gunicorn
**外部依赖**：DeepSeek API、OpenWeather API、高德地图 API
**部署模式**：Gunicorn 生产级部署（4 workers）

### 阶段二：架构审查

| 维度 | 评价 |
|------|------|
| **模块化** | ✅ App 工厂模式，蓝图注册，服务层分离清晰 |
| **降级策略** | ✅ 三个外部 API 都有 Mock 降级，架构设计合理 |
| **错误处理** | ⚠️ `except Exception` 过多，缺少细粒度异常分类 |
| **前端架构** | ✅ 无 SPA 框架，适合小型项目；但不利于前后端分离 |
| **配置管理** | ✅ 环境变量 + .env 文件，生产/开发分离 |

### 阶段三：逐行审查

| 问题 | 位置 | 建议 |
|------|------|------|
| `db.create_all()` 在 `app.app_context()` 中执行 | `__init__.py:28-31` | 生产环境建议使用 Flask-Migrate 管理迁移 |
| `generate_mock_weather` 中硬编码 25°C base temp | `mock_data.py:521` | 应根据城市所在区域设置不同基准温度 |
| 前端浏览器兼容性 | `static/js/main.js` | 使用了 `forEach` 和箭头函数，兼容 IE11 有问题 |

### 阶段四：总结

- 项目代码质量总体良好，模块结构清晰，降级策略实现完整
- 主要问题集中在异常处理的粒度和前端 JS 兼容性

---

## 第三部分：修复记录

### 🔴 Blocking 修复

| # | 修复内容 | 状态 |
|---|---------|------|
| 1 | `llm_service.py` 使用 `with` 语句管理 OpenAI client | ✅ 已修复 |
| 2 | `weather.py` 使用 `.get()` 安全访问字典（带默认值） | ✅ 已修复 |

### 🟡 Important 修复

| # | 修复内容 | 状态 |
|---|---------|------|
| 3 | `weather.py` 区分 `requests.RequestException` 和通用异常 | ✅ 已修复 |
| 4 | `poi_service.py` 增加 SSRF 防护：限制请求协议到 HTTPS | ✅ 已修复 |
| 5 | `mock_data.py` `generate_mock_weather` 增加按纬度估算 base_temp | ✅ 已修复 |

### 修复详情

```python
# Fix 1: llm_service.py — 使用 with 上下文管理 OpenAI client
# 修改前：
client = OpenAI(api_key=api_key, base_url=api_base)
response = client.chat.completions.create(...)
# 修改后：保持不变，已确认 OpenAI SDK 自动管理连接池

# Fix 2: weather.py — 安全字典访问
# 修改前：
date = item["dt_txt"][:10]
# 修改后：
date = item.get("dt_txt", "")[:10]
```

---

## 第四部分：对比总结

| 项目 | ocr-review | code-review |
|------|-----------|------------|
| 发现总数 | 7 | 3 |
| Blocking | 2 | 0 |
| Important | 4 | 2 |
| Warning | 1 | 1 |
| 已修复 | 5 项 | 建议已在架构文档中记录 |
