"""Main route blueprint for the Travel Planner application."""
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, abort
from travel_planner import db, limiter
from travel_planner.models import Itinerary
from travel_planner.services.llm_service import generate_itinerary
from travel_planner.services.weather import get_weather

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


def _fetch_weather(city, days):
    """Fetch weather data safely, returning empty list on failure."""
    try:
        return get_weather(city, days)
    except Exception as e:
        logger.warning(f"Weather fetch failed for {city}: {e}")
        return []


@main_bp.route("/")
def index():
    """Home page with the itinerary generation form."""
    return render_template("index.html")


@main_bp.route("/generate", methods=["POST"])
@limiter.limit("5 per minute")
def generate():
    """Handle itinerary generation form submission."""
    destination = request.form.get("destination", "").strip()
    days = request.form.get("days", 3, type=int)
    budget = request.form.get("budget", 3000, type=int)
    preferences = request.form.get("preferences", "").strip()

    if not destination:
        return redirect(url_for("main.index"))

    # Clamp values
    days = max(1, min(7, days))
    budget = max(500, budget)

    # Generate itinerary
    raw_data = generate_itinerary(destination, days, budget, preferences)

    # Save to database
    itinerary = Itinerary(
        destination=destination,
        days=days,
        budget=budget,
        preferences=preferences,
        raw_data=raw_data,
    )
    db.session.add(itinerary)
    db.session.commit()

    # Redirect via share token to prevent ID enumeration
    return redirect(url_for("main.share_itinerary", token=itinerary.share_token))


@main_bp.route("/itinerary/<int:id>")
def view_itinerary(id):
    """View a specific itinerary (maintained for history links)."""
    itinerary = Itinerary.query.get_or_404(id)
    data = itinerary.to_dict()

    # Fetch weather data
    weather_data = _fetch_weather(itinerary.destination, itinerary.days)

    return render_template(
        "itinerary.html",
        itinerary=itinerary,
        data=data,
        weather=weather_data,
    )


@main_bp.route("/share/<token>")
def share_itinerary(token):
    """View a shared itinerary via share token."""
    itinerary = Itinerary.query.filter_by(share_token=token).first_or_404()
    data = itinerary.to_dict()

    # Fetch weather data
    weather_data = _fetch_weather(itinerary.destination, itinerary.days)

    return render_template(
        "share.html",
        itinerary=itinerary,
        data=data,
        weather=weather_data,
    )


@main_bp.route("/history")
def history():
    """View past itineraries with pagination."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        Itinerary.query.order_by(Itinerary.created_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    return render_template(
        "history.html",
        itineraries=pagination.items,
        pagination=pagination,
    )
