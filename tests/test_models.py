"""Tests for the Itinerary model."""
import json
import pytest
from travel_planner.models import Itinerary


class TestItineraryModel:
    def test_create_itinerary(self, db, sample_itinerary_json):
        itinerary = Itinerary(
            destination="shanghai", days=3, budget=5000,
            preferences="shopping,food", raw_data=sample_itinerary_json,
        )
        db.session.add(itinerary)
        db.session.commit()
        assert itinerary.id is not None
        assert itinerary.destination == "shanghai"
        assert itinerary.days == 3
        assert itinerary.budget == 5000
        assert itinerary.share_token is not None
        assert len(itinerary.share_token) == 36

    def test_to_dict_returns_expected_keys(self, sample_itinerary):
        d = sample_itinerary.to_dict()
        assert d["id"] == sample_itinerary.id
        assert d["destination"] == "beijing"
        assert d["days"] == 3
        assert d["budget"] == 3000
        assert d["share_token"] == sample_itinerary.share_token
        assert "itinerary_days" in d
        assert "summary" in d
        assert "tips" in d
        assert isinstance(d["days"], int)
        assert d["days"] == 3

    def test_to_dict_contains_days_array(self, sample_itinerary):
        d = sample_itinerary.to_dict()
        assert isinstance(d["itinerary_days"], list)
        assert len(d["itinerary_days"]) == 1
        first_day = d["itinerary_days"][0]
        assert first_day["day_number"] == 1
        assert "spots" in first_day
        assert "meals" in first_day
        assert "accommodation" in first_day

    def test_to_dict_handles_bad_json(self, sample_itinerary_with_bad_json):
        d = sample_itinerary_with_bad_json.to_dict()
        assert d["destination"] == "beijing"
        assert d["itinerary_days"] == []
        assert d["summary"] == {}
        assert d["tips"] == []

    def test_to_dict_handles_null_raw_data(self, db):
        itinerary = Itinerary(destination="test", days=1, budget=1000, raw_data="")
        db.session.add(itinerary)
        db.session.commit()
        d = itinerary.to_dict()
        assert d["destination"] == "test"
        assert d["itinerary_days"] == []

    def test_share_token_is_unique(self, db, sample_itinerary_json):
        i1 = Itinerary(destination="beijing", days=1, budget=1000, raw_data=sample_itinerary_json)
        i2 = Itinerary(destination="shanghai", days=2, budget=2000, raw_data=sample_itinerary_json)
        db.session.add(i1)
        db.session.add(i2)
        db.session.commit()
        assert i1.share_token != i2.share_token

    def test_summary_content(self, sample_itinerary):
        d = sample_itinerary.to_dict()
        summary = d["summary"]
        assert summary["total_budget"] == 3000
        assert "estimated_total" in summary
        assert "spots_cost" in summary
        assert "meal_cost" in summary
        assert "accommodation_cost" in summary
        assert "transport_cost" in summary
