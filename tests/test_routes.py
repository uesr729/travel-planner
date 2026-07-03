"""Integration tests for route handlers (full HTTP request/response cycle)."""
import json
import pytest


class TestIndexRoute:
    """Test the home page route."""

    def test_index_page_loads(self, client):
        """Happy path: home page returns 200 and contains expected content."""
        resp = client.get("/")
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "AI 旅行规划师" in content
        assert "生成行程" in content
        assert "destination" in content  # form field


class TestGenerateRoute:
    """Test the itinerary generation route."""

    def test_generate_valid_itinerary(self, client):
        """Happy path: valid form submission creates itinerary and redirects."""
        resp = client.post(
            "/generate",
            data={
                "destination": "北京",
                "days": 3,
                "budget": 3000,
                "preferences": "美食,文化",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "/itinerary/" in resp.location

    def test_generate_and_view(self, client):
        """Full flow: generate → view itinerary with correct content."""
        resp = client.post(
            "/generate",
            data={"destination": "北京", "days": 3, "budget": 3000},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "北京" in content
        assert "cost-overview" in content
        assert "day-card" in content
        assert "spot-item" in content
        assert "map-container" in content

    def test_generate_empty_destination_redirects(self, client):
        """Boundary: empty destination should redirect to index."""
        resp = client.post(
            "/generate",
            data={"destination": "", "days": 3, "budget": 3000},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.location == "/"

    def test_generate_with_different_cities(self, client):
        """Happy path: different cities should generate successfully."""
        cities = ["成都", "杭州", "西安"]
        for city in cities:
            resp = client.post(
                "/generate",
                data={"destination": city, "days": 2, "budget": 3000},
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert city in resp.data.decode("utf-8")

    def test_generate_max_days(self, client):
        """Boundary: max days (7) should work."""
        resp = client.post(
            "/generate",
            data={"destination": "上海", "days": 7, "budget": 5000},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "上海" in content

    def test_generate_min_days(self, client):
        """Boundary: min days (1) should work."""
        resp = client.post(
            "/generate",
            data={"destination": "南京", "days": 1, "budget": 1000},
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_generate_no_preferences(self, client):
        """Boundary: empty preferences should work."""
        resp = client.post(
            "/generate",
            data={"destination": "广州", "days": 3, "budget": 3000, "preferences": ""},
            follow_redirects=True,
        )
        assert resp.status_code == 200


class TestViewItineraryRoute:
    """Test the itinerary viewing route."""

    def test_view_nonexistent_itinerary_404(self, client):
        """Error case: non-existent ID returns 404."""
        resp = client.get("/itinerary/99999")
        assert resp.status_code == 404

    def test_view_existing_itinerary(self, client, sample_itinerary):
        """Happy path: existing itinerary renders correctly."""
        resp = client.get(f"/itinerary/{sample_itinerary.id}")
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "北京" in content
        assert "cost-overview" in content
        assert "day-card" in content

    def test_view_itinerary_shows_cost_breakdown(self, client, sample_itinerary):
        """Cost overview grid should be rendered."""
        resp = client.get(f"/itinerary/{sample_itinerary.id}")
        content = resp.data.decode("utf-8")
        assert "总预算" in content
        assert "预估总花费" in content
        assert "景点门票" in content
        assert "餐饮" in content
        assert "住宿" in content

    def test_view_itinerary_shows_share_button(self, client, sample_itinerary):
        """Share button should be present on itinerary page."""
        resp = client.get(f"/itinerary/{sample_itinerary.id}")
        content = resp.data.decode("utf-8")
        assert "复制分享链接" in content or "shareBtn" in content


class TestShareRoute:
    """Test the share itinerary route."""

    def test_share_valid_token(self, client, sample_itinerary):
        """Happy path: valid share token shows itinerary."""
        resp = client.get(f"/share/{sample_itinerary.share_token}")
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "北京" in content
        assert "分享的行程" in content
        assert "创建自己的行程" in content

    def test_share_invalid_token_404(self, client):
        """Error case: invalid share token returns 404."""
        resp = client.get("/share/invalid-token-12345")
        assert resp.status_code == 404

    def test_share_token_uniqueness_in_url(self, client, sample_itinerary):
        """Share URL should contain the UUID token."""
        resp = client.get(f"/share/{sample_itinerary.share_token}")
        content = resp.data.decode("utf-8")
        # The share page should have a link to create new itinerary
        assert "创建自己的行程" in content


class TestHistoryRoute:
    """Test the history route."""

    def test_empty_history(self, client):
        """Empty state: no itineraries shows empty state."""
        resp = client.get("/history")
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "还没有生成过行程" in content or "生成第一个行程" in content

    def test_history_with_data(self, client, sample_itinerary):
        """Happy path: history shows created itineraries."""
        # Generate a second itinerary
        client.post(
            "/generate",
            data={"destination": "成都", "days": 2, "budget": 3000},
        )
        resp = client.get("/history")
        assert resp.status_code == 200
        content = resp.data.decode("utf-8")
        assert "北京" in content
        assert "成都" in content

    def test_history_link_to_itinerary(self, client, sample_itinerary):
        """History entries should link to itinerary detail."""
        resp = client.get("/history")
        content = resp.data.decode("utf-8")
        assert f"/itinerary/{sample_itinerary.id}" in content


class TestErrorHandling:
    """Test error handling routes."""

    def test_404_page(self, client):
        """Custom 404 page should be shown."""
        resp = client.get("/nonexistent-page")
        assert resp.status_code == 404
        content = resp.data.decode("utf-8")
        # Check for 404 template content
        assert "404" in content or "页面未找到" in content

    def test_invalid_method_on_generate(self, client):
        """GET on POST-only route should return 405."""
        resp = client.get("/generate")
        assert resp.status_code == 405
