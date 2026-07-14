"""Pytest configuration and shared fixtures."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from travel_planner import create_app, db as _db
from travel_planner.models import Itinerary


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture
def sample_itinerary_json():
    import json
    return json.dumps({
        "days": [{
            "day_number": 1,
            "title": "day1",
            "spots": [{"name": "spot1", "time_slot": "morning", "start_time": "08:00", "end_time": "12:00", "description": "desc", "cost": 0.0, "lat": 39.9, "lng": 116.4, "category": "sight", "duration_hours": 2.5}],
            "meals": [{"type": "lunch", "recommendation": "noodles", "restaurant": "noodles", "cost": 30.0}],
            "accommodation": {"name": "hotel", "cost": 300, "note": "breakfast"}
        }],
        "summary": {"total_budget": 3000, "estimated_total": 1500, "spots_cost": 60, "meal_cost": 180, "accommodation_cost": 300, "transport_cost": 100, "other_cost": 0},
        "tips": ["tip1", "tip2"]
    }, ensure_ascii=False)


@pytest.fixture
def sample_itinerary(db, sample_itinerary_json):
    itinerary = Itinerary(destination="beijing", days=3, budget=3000, preferences="food", raw_data=sample_itinerary_json)
    db.session.add(itinerary)
    db.session.commit()
    return itinerary


@pytest.fixture
def sample_itinerary_with_bad_json(db):
    itinerary = Itinerary(destination="beijing", days=3, budget=3000, preferences="food", raw_data="not valid json{{{")
    db.session.add(itinerary)
    db.session.commit()
    return itinerary
