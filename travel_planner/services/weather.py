"""Weather service for the Travel Planner application.

Fetches weather data from OpenWeather API. Falls back to mock data on failure.
Now supports any city name directly (not limited to a hardcoded list).
"""
import logging
from typing import Optional
import requests
from flask import current_app
from travel_planner.services.mock_data import generate_mock_weather

logger = logging.getLogger(__name__)


def get_weather(city: str, days: int = 3) -> list:
    """Fetch weather forecast for a city by city name (not a hardcoded ID list).

    Uses the 'q' parameter of OpenWeather API to support any city in the world.
    Falls back to mock data on failure (network, unknown city, etc.)

    Returns a list of dicts with keys: date, temp, temp_high, temp_low, weather, icon, humidity
    """
    api_key = current_app.config.get("OPENWEATHER_API_KEY", "")

    if not api_key:
        logger.info("OPENWEATHER_API_KEY not configured, using mock weather")
        return generate_mock_weather(city, days)

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
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
        logger.warning(f"Weather API call failed for '{city}': {e}, using mock weather")
        return generate_mock_weather(city, days)
