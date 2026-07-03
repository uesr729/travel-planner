"""Weather service for the Travel Planner application.

Fetches weather data from OpenWeather API. Falls back to mock data on failure.
"""
import logging
from typing import Optional
import requests
from flask import current_app
from travel_planner.services.mock_data import generate_mock_weather

logger = logging.getLogger(__name__)

# Chinese city name to OpenWeather city ID mapping
CITY_IDS = {
    "北京": 1816670,
    "上海": 1796236,
    "广州": 1809858,
    "深圳": 1795565,
    "成都": 1815286,
    "杭州": 1799397,
    "西安": 1793505,
    "重庆": 1814906,
    "武汉": 1793347,
    "南京": 1799962,
    "苏州": 1796949,
    "昆明": 1804849,
    "三亚": 1886760,
    "厦门": 1816971,
    "青岛": 1797929,
    "大连": 1814087,
    "长沙": 1814870,
    "哈尔滨": 1807686,
    "拉萨": 1280737,
    "桂林": 1809482,
}


def get_weather(city: str, days: int = 3) -> list:
    """Fetch weather forecast for a city.

    First attempts to call OpenWeather API. Falls back to mock data on failure.

    Returns a list of dicts with keys: date, temp, temp_high, temp_low, weather, icon, humidity
    """
    api_key = current_app.config.get("OPENWEATHER_API_KEY", "")

    if not api_key:
        logger.info("OPENWEATHER_API_KEY not configured, using mock weather")
        return generate_mock_weather(city, days)

    city_id = CITY_IDS.get(city)
    if not city_id:
        logger.info(f"City '{city}' not in mapping, using mock weather")
        return generate_mock_weather(city, days)

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "id": city_id,
            "appid": api_key,
            "units": "metric",
            "lang": "zh_cn",
        }

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()

        data = resp.json()

        # Process forecast, one entry per day
        daily = {}
        for item in data.get("list", []):
            date = item["dt_txt"][:10]
            if date not in daily:
                daily[date] = {
                    "temp": item["main"]["temp"],
                    "temp_high": item["main"]["temp_max"],
                    "temp_low": item["main"]["temp_min"],
                    "weather": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"],
                    "humidity": item["main"]["humidity"],
                }

        result = []
        for i, (date, weather) in enumerate(
            list(daily.items())[:days]
        ):
            result.append({"date": date, **weather})

        return result

    except Exception as e:
        logger.warning(f"Weather API call failed: {e}, using mock weather")
        return generate_mock_weather(city, days)
