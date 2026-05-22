"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # AI Model
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514")

    # Strava
    STRAVA_CLIENT_ID: str = os.getenv("STRAVA_CLIENT_ID", "")
    STRAVA_CLIENT_SECRET: str = os.getenv("STRAVA_CLIENT_SECRET", "")
    STRAVA_REDIRECT_URI: str = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/auth/strava/callback")

    # TrainingPeaks
    TRAININGPEAKS_CLIENT_ID: str = os.getenv("TRAININGPEAKS_CLIENT_ID", "")
    TRAININGPEAKS_CLIENT_SECRET: str = os.getenv("TRAININGPEAKS_CLIENT_SECRET", "")
    TRAININGPEAKS_REDIRECT_URI: str = os.getenv(
        "TRAININGPEAKS_REDIRECT_URI", "http://localhost:8000/auth/trainingpeaks/callback"
    )

    # Garmin
    GARMIN_CONNECT_EMAIL: str = os.getenv("GARMIN_CONNECT_EMAIL", "")
    GARMIN_CONNECT_PASSWORD: str = os.getenv("GARMIN_CONNECT_PASSWORD", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fitagent.db")

    # App
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))


settings = Settings()
