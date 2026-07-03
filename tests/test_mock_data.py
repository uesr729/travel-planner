"""Tests for mock data service."""
import json
import pytest
from travel_planner.services.mock_data import (
    CITY_COORDS,
    CITY_DATA,
    get_city_coords,
    generate_mock_itinerary,
    generate_mock_weather,
)


class TestCityCoordinates:
    """Test city coordinate database."""

    def test_known_city_has_coords(self):
        """Happy path: known cities have coordinates."""
        coords = get_city_coords("北京")
        assert coords is not None
        assert "lat" in coords
        assert "lng" in coords
        assert isinstance(coords["lat"], float)
        assert isinstance(coords["lng"], float)

    def test_unknown_city_returns_none(self):
        """Boundary: unknown cities return None."""
        coords = get_city_coords("虚构城市")
        assert coords is None

    def test_city_count(self):
        """We should have at least 20 cities in the database."""
        assert len(CITY_COORDS) >= 20

    def test_city_data_has_5_core_cities(self):
        """5 core cities should have detailed data."""
        core_cities = ["北京", "上海", "成都", "西安", "杭州"]
        for city in core_cities:
            assert city in CITY_DATA, f"Missing city data for {city}"
            assert "spots" in CITY_DATA[city]
            assert "restaurants" in CITY_DATA[city]
            assert "accommodations" in CITY_DATA[city]


class TestMockItineraryGeneration:
    """Test mock itinerary generation."""

    def test_generate_mock_itinerary_returns_valid_json(self):
        """Happy path: generates valid JSON string."""
        result = generate_mock_itinerary("北京", 3, 3000, "美食")
        data = json.loads(result)
        assert "days" in data
        assert "summary" in data
        assert "tips" in data

    def test_generate_correct_number_of_days(self):
        """Happy path: generates correct number of days."""
        for days in [1, 3, 5, 7]:
            result = generate_mock_itinerary("成都", days, 3000)
            data = json.loads(result)
            assert len(data["days"]) == days, f"Expected {days} days, got {len(data['days'])}"

    def test_day_contains_required_fields(self):
        """Each day should have all required fields."""
        result = generate_mock_itinerary("西安", 3, 3000)
        data = json.loads(result)
        for day in data["days"]:
            assert "day_number" in day
            assert "title" in day
            assert "spots" in day
            assert "meals" in day
            assert len(day["spots"]) > 0

    def test_spot_contains_coordinates(self):
        """Each spot should have valid lat/lng coordinates."""
        result = generate_mock_itinerary("杭州", 3, 3000)
        data = json.loads(result)
        for day in data["days"]:
            for spot in day["spots"]:
                assert "lat" in spot
                assert "lng" in spot
                assert isinstance(spot["lat"], (int, float))
                assert isinstance(spot["lng"], (int, float))
                # Coordinates should be reasonable Chinese city coordinates
                assert 20 <= spot["lat"] <= 45
                assert 100 <= spot["lng"] <= 125

    def test_summary_math(self):
        """Summary costs should be calculated reasonably."""
        result = generate_mock_itinerary("北京", 3, 3000)
        data = json.loads(result)
        summary = data["summary"]
        assert summary["total_budget"] == 3000
        assert summary["estimated_total"] > 0
        # Cost breakdown should sum to roughly estimated total
        total_breakdown = (
            summary["spots_cost"]
            + summary["meal_cost"]
            + summary["accommodation_cost"]
            + summary["transport_cost"]
            + summary.get("other_cost", 0)
        )
        assert abs(total_breakdown - summary["estimated_total"]) < 500

    def test_unknown_city_falls_back_to_beijing(self):
        """Boundary: unknown city should fall back to Beijing data."""
        result = generate_mock_itinerary("虚构城市", 3, 3000)
        data = json.loads(result)
        assert len(data["days"]) == 3
        assert data["summary"]["total_budget"] == 3000

    def test_empty_preferences(self):
        """Boundary: empty preferences should not cause errors."""
        result = generate_mock_itinerary("成都", 3, 3000, "")
        data = json.loads(result)
        assert len(data["days"]) == 3

    def test_minimal_input(self):
        """Boundary: 1 day, min budget."""
        result = generate_mock_itinerary("西安", 1, 500)
        data = json.loads(result)
        assert len(data["days"]) == 1


class TestMockWeather:
    """Test mock weather generation."""

    def test_generate_weather_returns_list(self):
        """Happy path: returns a list of weather dicts."""
        weather = generate_mock_weather("北京", 3)
        assert isinstance(weather, list)
        assert len(weather) == 3

    def test_weather_has_required_fields(self):
        """Each weather entry should have required fields."""
        weather = generate_mock_weather("上海", 5)
        for w in weather:
            assert "date" in w
            assert "temp" in w
            assert "temp_high" in w
            assert "temp_low" in w
            assert "weather" in w
            assert "humidity" in w

    def test_weather_temp_is_reasonable(self):
        """Temperature should be within reasonable range."""
        weather = generate_mock_weather("北京", 3)
        for w in weather:
            assert -20 <= w["temp"] <= 50
            assert w["temp_low"] <= w["temp_high"]

    def test_unknown_city_weather(self):
        """Boundary: unknown city should still generate weather."""
        weather = generate_mock_weather("虚构城市", 3)
        assert len(weather) == 3
