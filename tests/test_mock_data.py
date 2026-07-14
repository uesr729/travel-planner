"""Tests for mock data service."""
import json
import pytest
from travel_planner.services.mock_data import (
    CITY_COORDS, CITY_DATA, get_city_coords,
    generate_mock_itinerary, generate_mock_weather,
)


class TestCityCoordinates:
    def test_known_city_has_coords(self):
        coords = get_city_coords("beijing")
        assert coords is not None
        assert "lat" in coords
        assert "lng" in coords

    def test_unknown_city_returns_none(self):
        coords = get_city_coords("fakecity")
        assert coords is None

    def test_city_count(self):
        assert len(CITY_COORDS) >= 20

    def test_city_data_has_5_core_cities(self):
        core_cities = ["beijing", "shanghai", "chengdu", "xian", "hangzhou"]
        for city in core_cities:
            assert city in CITY_DATA
            assert "spots" in CITY_DATA[city]
            assert "restaurants" in CITY_DATA[city]
            assert "accommodations" in CITY_DATA[city]


class TestMockItineraryGeneration:
    def test_generate_mock_itinerary_returns_valid_json(self):
        result = generate_mock_itinerary("beijing", 3, 3000, "food")
        data = json.loads(result)
        assert "days" in data
        assert "summary" in data
        assert "tips" in data

    def test_generate_correct_number_of_days(self):
        for days in [1, 3, 5, 7]:
            result = generate_mock_itinerary("chengdu", days, 3000)
            data = json.loads(result)
            assert len(data["days"]) == days

    def test_day_contains_required_fields(self):
        result = generate_mock_itinerary("xian", 3, 3000)
        data = json.loads(result)
        for day in data["days"]:
            assert "day_number" in day
            assert "title" in day
            assert "spots" in day
            assert "meals" in day
            assert len(day["spots"]) > 0

    def test_spot_contains_coordinates(self):
        result = generate_mock_itinerary("hangzhou", 3, 3000)
        data = json.loads(result)
        for day in data["days"]:
            for spot in day["spots"]:
                assert "lat" in spot
                assert "lng" in spot
                assert 20 <= spot["lat"] <= 45
                assert 100 <= spot["lng"] <= 125

    def test_summary_math(self):
        result = generate_mock_itinerary("beijing", 3, 3000)
        data = json.loads(result)
        summary = data["summary"]
        assert summary["total_budget"] == 3000
        assert summary["estimated_total"] > 0

    def test_unknown_city_falls_back(self):
        result = generate_mock_itinerary("fakecity", 3, 3000)
        data = json.loads(result)
        assert len(data["days"]) == 3

    def test_empty_preferences(self):
        result = generate_mock_itinerary("chengdu", 3, 3000, "")
        data = json.loads(result)
        assert len(data["days"]) == 3

    def test_minimal_input(self):
        result = generate_mock_itinerary("xian", 1, 500)
        data = json.loads(result)
        assert len(data["days"]) == 1


class TestMockWeather:
    def test_generate_weather_returns_list(self):
        weather = generate_mock_weather("beijing", 3)
        assert isinstance(weather, list)
        assert len(weather) == 3

    def test_weather_has_required_fields(self):
        weather = generate_mock_weather("shanghai", 5)
        for w in weather:
            assert "date" in w
            assert "temp" in w
            assert "temp_high" in w
            assert "temp_low" in w
            assert "weather" in w
            assert "humidity" in w

    def test_weather_temp_is_reasonable(self):
        weather = generate_mock_weather("beijing", 3)
        for w in weather:
            assert -20 <= w["temp"] <= 50
            assert w["temp_low"] <= w["temp_high"]

    def test_unknown_city_weather(self):
        weather = generate_mock_weather("fakecity", 3)
        assert len(weather) == 3
