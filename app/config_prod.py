import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class ProductionConfig:
    """
    Production configuration for Toubina (AI Solute)
    """

    # --------------------------------------------------
    # Security
    # --------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is required for production")

    DEBUG = False
    TESTING = False

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is required for production")

    # Fix Heroku / Render postgres:// issue
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------------------------------------
    # Uploads
    # --------------------------------------------------
    if os.environ.get("RENDER") or os.environ.get("DYNO"):
        UPLOAD_FOLDER = Path("/tmp/uploads")
    else:
        UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
