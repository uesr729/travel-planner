"""Pytest configuration and shared fixtures."""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from travel_planner import create_app, db as _db
from travel_planner.models import Itinerary


@pytest.fixture
def app():
    """Create a test Flask application with in-memory SQLite."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Provide the database instance within app context."""
    with app.app_context():
        yield _db


@pytest.fixture
def sample_itinerary_json():
    """Return a sample itinerary JSON string for testing."""
    import json

    return json.dumps(
        {
            "days": [
                {
                    "day_number": 1,
                    "title": "第1天 — 北京探索之旅",
                    "spots": [
                        {
                            "name": "天安门广场",
                            "time_slot": "上午",
                            "start_time": "08:00",
                            "end_time": "12:00",
                            "description": "世界上最大的城市广场",
                            "cost": 0.0,
                            "lat": 39.9042,
                            "lng": 116.3974,
                            "category": "景点",
                            "duration_hours": 2.5,
                        }
                    ],
                    "meals": [
                        {
                            "type": "午餐",
                            "recommendation": "炸酱面馆",
                            "restaurant": "炸酱面馆",
                            "cost": 30.0,
                        }
                    ],
                    "accommodation": {
                        "name": "北京市中心酒店",
                        "cost": 300,
                        "note": "含早餐",
                    },
                }
            ],
            "summary": {
                "total_budget": 3000,
                "estimated_total": 1500,
                "spots_cost": 60,
                "meal_cost": 180,
                "accommodation_cost": 300,
                "transport_cost": 100,
                "other_cost": 0,
            },
            "tips": ["提前预订门票", "注意天气变化"],
        },
        ensure_ascii=False,
    )


@pytest.fixture
def sample_itinerary(db, sample_itinerary_json):
    """Create a sample Itinerary in the test database."""
    itinerary = Itinerary(
        destination="北京",
        days=3,
        budget=3000,
        preferences="美食",
        raw_data=sample_itinerary_json,
    )
    db.session.add(itinerary)
    db.session.commit()
    return itinerary


@pytest.fixture
def sample_itinerary_with_bad_json(db):
    """Create an Itinerary with corrupted raw_data."""
    itinerary = Itinerary(
        destination="北京",
        days=3,
        budget=3000,
        preferences="美食",
        raw_data="not valid json{{{",
    )
    db.session.add(itinerary)
    db.session.commit()
    return itinerary
