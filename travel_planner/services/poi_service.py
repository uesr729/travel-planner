"""POI (Point of Interest) service for the Travel Planner application.

Fetches real attraction/location data from Amap (高德地图) Web API.
Falls back to empty results on failure.
"""
import json
import logging
from typing import Optional
from urllib.parse import quote
import requests
from flask import current_app

logger = logging.getLogger(__name__)


# POI type codes for "景点" (scenic spots / tourist attractions)
AMAP_SCENIC_TYPES = "110000"  # 风景名胜大类
AMAP_SCENIC_KEYWORDS = ["景点", "风景区", "公园", "博物馆", "老街", "古镇", "寺庙"]


def search_attractions(city: str) -> list:
    """Search for real attractions in a city using Amap POI API.

    Makes multiple queries with different keywords to get diverse results,
    then deduplicates and returns a unified list.

    Returns a list of dicts with keys:
        name, lat, lng, address, cost (always 0 for free, estimate if ticket exists),
        category, description
    Returns empty list if API key not configured or request fails.
    """
    api_key = current_app.config.get("AMAP_API_KEY", "")

    if not api_key:
        logger.info("AMAP_API_KEY not configured, skipping real POI search")
        return []

    # Try different keyword combinations to get diverse results
    all_results = {}
    keywords_to_try = AMAP_SCENIC_KEYWORDS[:4]  # Use first 4 keywords

    for keyword in keywords_to_try:
        results = _amap_text_search(api_key, keyword, city)
        for poi in results:
            # Deduplicate by name
            name = poi.get("name", "")
            if name and name not in all_results:
                all_results[name] = poi

    if not all_results:
        # Fallback: try without type filter, just keyword search
        results = _amap_text_search(api_key, "景点", city, types="")
        for poi in results:
            name = poi.get("name", "")
            if name and name not in all_results:
                all_results[name] = poi

    # Filter out results with invalid coordinates (lat=0, lng=0)
    valid_results = [
        p for p in all_results.values()
        if abs(p.get("lat", 0)) > 0.001 or abs(p.get("lng", 0)) > 0.001
    ]

    logger.info(
        f"Found {len(all_results)} unique POIs for '{city}' via Amap API "
        f"({len(valid_results)} with valid coordinates)"
    )
    return valid_results


def _amap_text_search(
    api_key: str,
    keywords: str,
    city: str,
    types: str = AMAP_SCENIC_TYPES,
    page_size: int = 20,
    page_num: int = 1,
) -> list:
    """Call Amap text search API for POI data.

    https://restapi.amap.com/v3/place/text
    """
    try:
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "key": api_key,
            "keywords": keywords,
            "city": city,
            "offset": page_size,
            "page": page_num,
            "extensions": "all",
            "output": "json",
        }
        if types:
            params["types"] = types

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()

        data = resp.json()

        if data.get("status") != "1":
            logger.warning(
                f"Amap API error for '{keywords}' in '{city}': "
                f"{data.get('info', 'unknown error')}"
            )
            return []

        pois = data.get("pois", [])
        return [_convert_amap_poi(poi) for poi in pois]

    except Exception as e:
        logger.warning(
            f"Amap API request failed for '{keywords}' in '{city}': {e}"
        )
        return []


def _convert_amap_poi(poi: dict) -> dict:
    """Convert Amap POI format to our internal format."""
    name = poi.get("name", "")
    address = poi.get("address", "")
    category = _simplify_category(poi.get("type", ""))

    # Parse location string "lng,lat"
    location = poi.get("location", "")
    lat = 0.0
    lng = 0.0
    if location and "," in location:
        parts = location.split(",")
        try:
            lng = float(parts[0])
            lat = float(parts[1])
        except (ValueError, IndexError):
            pass

    # Estimate cost based on category and name
    estimated_cost = _estimate_cost(name, category)

    # Build description
    desc_parts = []
    if address:
        desc_parts.append(address)
    if category:
        desc_parts.append(category)
    description = "，".join(desc_parts) if desc_parts else f"{name} — {category}"

    return {
        "name": name,
        "lat": lat,
        "lng": lng,
        "cost": estimated_cost,
        "category": category,
        "description": description,
    }


def _simplify_category(amap_type: str) -> str:
    """Simplify Amap's hierarchical type (e.g. '风景名胜;风景名胜;风景区')
    to a short category name."""
    simplified_map = {
        "风景名胜": "景点",
        "公园广场": "自然",
        "博物馆": "文化",
        "纪念馆": "历史",
        "寺庙": "历史",
        "教堂": "文化",
        "展览馆": "文化",
        "美术馆": "艺术",
        "图书馆": "文化",
        "购物": "购物",
        "步行街": "购物",
        "商业街": "购物",
        "美食": "美食",
        "餐饮": "美食",
        "自然地物": "自然",
        "湖泊": "自然",
        "山": "自然",
        "海滩": "自然",
        "历史": "历史",
        "人文": "文化",
    }

    # Amap type is hierarchical, e.g. "风景名胜;风景名胜;风景区"
    parts = amap_type.split(";")
    for part in parts:
        part = part.strip()
        if part in simplified_map:
            return simplified_map[part]

    # Return first non-empty part
    for part in parts:
        if part.strip():
            return part.strip()

    return "景点"


def _estimate_cost(name: str, category: str) -> int:
    """Roughly estimate ticket cost based on POI name and category."""
    name_lower = name.lower()

    # Free categories
    if category in ("购物", "美食", "自然"):
        return 0

    # Common free keywords in name
    free_keywords = ["公园", "广场", "街", "步行街", "海滩", "湖", "江", "河", "滨江"]
    for kw in free_keywords:
        if kw in name:
            return 0

    # Museums, exhibitions: usually 20-60
    if category in ("文化", "艺术", "博物馆"):
        return 30

    # Historical sites: 20-80
    if category in ("历史", "寺庙", "教堂"):
        return 40

    # Scenic spots: 0-200
    if category == "景点":
        major_scenic = ["风景", "景区", "名胜"]
        for kw in major_scenic:
            if kw in name:
                return 80
        return 30

    return 0
