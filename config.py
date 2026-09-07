import os


class Config:
    """Zentrale Flask-Konfiguration."""

    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY",
        "change-this-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///love_yourself.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_USERNAME = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    ).strip()
