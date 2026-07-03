# AI 旅行规划师 — Bug 分析与修复记录

## 概述

本次测试过程中，通过代码审查发现并修复了 4 个问题。测试执行阶段（43 个测试用例）未发现新的运行时 Bug。

---

## Bug 汇总表

| Bug ID | 问题描述 | 发现方式 | 严重程度 | 类型 | 状态 |
|--------|---------|---------|---------|------|------|
| BUG-001 | to_dict() raw_data 字段覆盖模型字段 | 代码审查 | **严重** | 逻辑缺陷 | ✅ 已修复 |
| BUG-002 | json.loads 无异常处理 | 代码审查 | **严重** | 错误处理缺失 | ✅ 已修复 |
| BUG-003 | 模板 XSS 风险 (tojson\|safe) | 代码审查 | **严重** | 安全漏洞 | ✅ 已修复 |
| BUG-004 | 天气获取代码重复 | 代码审查 | 中 | 代码复用 | ✅ 已修复 |

---

## 深入分析：BUG-001 — to_dict() 字段覆盖

### 问题现象

`Itinerary.to_dict()` 方法中，`**data`（raw_data 的展开）放在返回字典末尾，如果 raw_data JSON 中包含与模型字段同名的键（如 `id`、`days`、`destination`），会覆盖模型中的正确值。

### 复现步骤

1. 创建一个 Itinerary，其 raw_data 中包含 `"id": "malicious_string"` 或 `"days": [{"fake": "data"}]`
2. 调用 `itinerary.to_dict()`
3. 返回结果中 `id` 被覆盖为字符串，`days` 被覆盖为数组

### 根因分析

```python
# 问题代码
def to_dict(self):
    data = json.loads(self.raw_data)
    return {
        "id": self.id,              # 模型字段
        "destination": self.destination,
        "days": self.days,
        ...
        **data,                     # ← 放在最后，会覆盖上面的全部字段
    }
```

**根因**：Python 字典的 `**` 展开操作中，后面的键会覆盖前面的键。`**data` 放在最后导致 raw_data 中的所有键都会覆盖模型字段。

**归类**：编码疏忽。设计意图是将 raw_data 中的额外数据附加到返回字典中，但未考虑键名冲突。

### 修复方案

```python
def to_dict(self):
    import json
    try:
        data = json.loads(self.raw_data) if self.raw_data else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        data = {}

    return {
        "id": self.id,
        "destination": self.destination,
        "days": self.days,
        "budget": self.budget,
        "preferences": self.preferences,
        "share_token": self.share_token,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        # 只提取 raw_data 中预期的键，不覆盖模型字段
        "itinerary_days": data.get("days", []),
        "summary": data.get("summary", {}),
        "tips": data.get("tips", []),
    }
```

**关键改变**：
1. 添加 try/except 处理 JSON 解析异常
2. 检查空 raw_data
3. 从 raw_data 中只提取预期的键（days→itinerary_days、summary、tips）
4. 模型字段不会被任何 raw_data 中的值覆盖

### 影响范围

- **直接影响的视图函数**：`view_itinerary()` 和 `share_itinerary()` 都调用 `to_dict()`
- **涉及的模板**：itinerary.html 和 share.html 中对 `data.days` 的引用需要改为 `data.itinerary_days`
- **测试验证**：新增 `test_to_dict_handles_bad_json` 和 `test_to_dict_handles_null_raw_data` 两个测试用例验证修复

### 修复验证

```
✅ to_dict() 返回包含 itinerary_days/summary/tips 键
✅ 损坏的 raw_data 不导致 500 错误
✅ 空的 raw_data 返回空列表/空字典
✅ 模型字段（id/days/destination）不被覆盖
✅ 所有 43 个测试用例通过
```

---

## Bug 修复清单（按文件）

| 文件 | 修改内容 |
|------|---------|
| travel_planner/models.py | to_dict() 改用安全提取方式，添加异常处理 |
| travel_planner/templates/itinerary.html | data.days → data.itinerary_days；修复 XSS 风险 |
| travel_planner/templates/share.html | data.days → data.itinerary_days；修复 XSS 风险 |
| travel_planner/routes/main.py | 天气获取抽取为 _fetch_weather() 辅助函数 |
| travel_planner/__init__.py | 注册 404 错误处理器 |
