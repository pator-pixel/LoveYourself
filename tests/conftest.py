"""Gemeinsame pytest-Fixtures für die Love-Yourself-Anwendung."""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import User


@pytest.fixture()
def app(tmp_path):
    """Erstellt für jeden Test eine isolierte Flask-App mit eigener Datenbank."""

    database_path = tmp_path / "test.db"

    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
    })

    with test_app.app_context():
        db.drop_all()
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Flask-Testclient: simuliert Browseranfragen ohne echten Server."""
    return app.test_client()


@pytest.fixture()
def user(app):
    """Legt einen normalen Testbenutzer an."""
    with app.app_context():
        test_user = User(
            username="testperson",
            password_hash=generate_password_hash("Sicher123!"),
            language="de",
        )
        db.session.add(test_user)
        db.session.commit()
        user_id = test_user.id

    with app.app_context():
        yield db.session.get(User, user_id)
