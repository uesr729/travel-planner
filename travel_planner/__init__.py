"""Travel Planner Application Factory."""
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from travel_planner.routes.main import main_bp

    app.register_blueprint(main_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    # Create tables (development only; production uses Flask-Migrate)
    if os.getenv("FLASK_ENV", "development") == "development":
        with app.app_context():
            from travel_planner import models  # noqa: F401

            db.create_all()

    return app
