"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///travel_planner.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DeepSeek API
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE = os.getenv(
        "DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"
    )

    # OpenWeather API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
