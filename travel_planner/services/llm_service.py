"""LLM-based itinerary generation service.

Uses DeepSeek API (OpenAI-compatible) to generate structured travel itineraries.
Falls back to mock data when API is unavailable.
"""
import json
import logging
from typing import Optional
from openai import OpenAI
from flask import current_app
from travel_planner.services.mock_data import generate_mock_itinerary

logger = logging.getLogger(__name__)

# System prompt for itinerary generation
SYSTEM_PROMPT = """你是一个专业的旅行规划助手。请根据用户输入的目的地、天数、预算和偏好，生成一份详细、合理的旅行行程。

重要要求：
1. 必须输出严格的 JSON 格式，不要包含其他文字
2. 所有景点坐标必须使用真实的中国城市地理坐标
3. 费用标注必须合理，与预算匹配
4. 每日安排2-3个景点，不可过于紧凑

输出 JSON 格式：
{
  "days": [
    {
      "day_number": 1,
      "title": "第1天 — 城市探索之旅",
      "spots": [
        {
          "name": "景点名称",
          "time_slot": "上午/下午/晚上",
          "start_time": "08:00",
          "end_time": "12:00",
          "description": "景点描述",
          "cost": 0.0,
          "lat": 39.9042,
          "lng": 116.3974,
          "category": "景点/历史/美食/自然/购物/文化",
          "duration_hours": 2.5
        }
      ],
      "meals": [
        {
          "type": "早餐/午餐/晚餐",
          "recommendation": "推荐菜品说明",
          "restaurant": "餐厅名称",
          "cost": 30.0
        }
      ],
      "accommodation": {
        "name": "住宿名称",
        "cost": 300,
        "note": "住宿说明"
      }
    }
  ],
  "summary": {
    "total_budget": 3000,
    "estimated_total": 2500,
    "spots_cost": 300,
    "meal_cost": 500,
    "accommodation_cost": 1200,
    "transport_cost": 400,
    "other_cost": 100
  },
  "tips": [
    "实用旅行建议1",
    "实用旅行建议2"
  ]
}"""


def _build_user_prompt(destination: str, days: int, budget: int, preferences: str) -> str:
    """Build the user prompt for the LLM."""
    pref_text = preferences if preferences else "无特定偏好"
    return (
        f"请为以下旅行计划生成详细行程：\n"
        f"- 目的地：{destination}\n"
        f"- 天数：{days}天\n"
        f"- 预算：{budget}元\n"
        f"- 偏好：{pref_text}\n\n"
        f"请输出完整的 JSON 格式行程，包含每日景点（含真实坐标）、餐饮推荐、住宿推荐和费用明细。"
    )


def generate_itinerary(
    destination: str, days: int, budget: int, preferences: str = ""
) -> str:
    """Generate a travel itinerary.

    First attempts to call DeepSeek API. Falls back to mock data on failure.

    Returns a JSON string.
    """
    api_key = current_app.config.get("DEEPSEEK_API_KEY", "")
    api_base = current_app.config.get("DEEPSEEK_API_BASE", "")

    if not api_key:
        logger.info("DEEPSEEK_API_KEY not configured, using mock data")
        return generate_mock_itinerary(destination, days, budget, preferences)

    try:
        client = OpenAI(api_key=api_key, base_url=api_base)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_user_prompt(
                        destination, days, budget, preferences
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=4096,
            timeout=30,
        )

        content = response.choices[0].message.content.strip()

        # Try to parse as JSON to validate
        # Remove markdown code block if present
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0].strip()

        parsed = json.loads(content)
        # Add budget info to summary
        parsed.setdefault("summary", {})
        parsed["summary"]["total_budget"] = budget

        return json.dumps(parsed, ensure_ascii=False)

    except Exception as e:
        logger.warning(f"LLM API call failed: {e}, falling back to mock data")
        return generate_mock_itinerary(destination, days, budget, preferences)
