"""Integration tests for route handlers."""
import json
import pytest


class TestIndexRoute:
    def test_index_page_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200


class TestGenerateRoute:
    def test_generate_valid_itinerary(self, client):
        resp = client.post("/generate", data={
            "destination": "beijing", "days": 3, "budget": 3000, "preferences": "food,culture",
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/itinerary/" in resp.location

    def test_generate_and_view(self, client):
        resp = client.post("/generate", data={
            "destination": "beijing", "days": 3, "budget": 3000,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_generate_empty_destination_redirects(self, client):
        resp = client.post("/generate", data={
            "destination": "", "days": 3, "budget": 3000,
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.location == "/"

    def test_generate_with_different_cities(self, client):
        cities = ["chengdu", "hangzhou", "xian"]
        for city in cities:
            resp = client.post("/generate", data={
                "destination": city, "days": 2, "budget": 3000,
            }, follow_redirects=True)
            assert resp.status_code == 200

    def test_generate_max_days(self, client):
        resp = client.post("/generate", data={
            "destination": "shanghai", "days": 7, "budget": 5000,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_generate_min_days(self, client):
        resp = client.post("/generate", data={
            "destination": "nanjing", "days": 1, "budget": 1000,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_generate_no_preferences(self, client):
        resp = client.post("/generate", data={
            "destination": "guangzhou", "days": 3, "budget": 3000, "preferences": "",
        }, follow_redirects=True)
        assert resp.status_code == 200


class TestViewItineraryRoute:
    def test_view_nonexistent_itinerary_404(self, client):
        resp = client.get("/itinerary/99999")
        assert resp.status_code == 404

    def test_view_existing_itinerary(self, client, sample_itinerary):
        resp = client.get(f"/itinerary/{sample_itinerary.id}")
        assert resp.status_code == 200


class TestShareRoute:
    def test_share_valid_token(self, client, sample_itinerary):
        resp = client.get(f"/share/{sample_itinerary.share_token}")
        assert resp.status_code == 200

    def test_share_invalid_token_404(self, client):
        resp = client.get("/share/invalid-token-12345")
        assert resp.status_code == 404


class TestHistoryRoute:
    def test_empty_history(self, client):
        resp = client.get("/history")
        assert resp.status_code == 200

    def test_history_with_data(self, client, sample_itinerary):
        client.post("/generate", data={
            "destination": "chengdu", "days": 2, "budget": 3000,
        })
        resp = client.get("/history")
        assert resp.status_code == 200
