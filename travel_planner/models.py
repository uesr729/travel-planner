"""Data models for the Travel Planner application."""
import uuid
from datetime import datetime, timezone
from travel_planner import db


class Itinerary(db.Model):
    """Core model representing a generated travel itinerary."""

    __tablename__ = "itinerary"

    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(200), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    preferences = db.Column(db.String(500), default="")
    raw_data = db.Column(db.Text, nullable=False)  # JSON string
    share_token = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Convert model to a complete dictionary with parsed raw_data."""
        import json

        try:
            data = json.loads(self.raw_data) if self.raw_data else {}
        except (json.JSONDecodeError, TypeError, ValueError):
            data = {}

        return {
            "id": self.id,
            "destination": self.destination,
            "days": self.days,
            "budget": self.budget,
            "preferences": self.preferences,
            "share_token": self.share_token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Extract known keys from raw_data without overriding model fields
            "itinerary_days": data.get("days", []),
            "summary": data.get("summary", {}),
            "tips": data.get("tips", []),
        }

    def __repr__(self):
        return f"<Itinerary {self.id}: {self.destination} ({self.days}天)>"
