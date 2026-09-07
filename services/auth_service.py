from flask import current_app, session

from extensions import db
from models import User


def get_logged_in_user():
    """
    Gibt den aktuell angemeldeten Benutzer zurück.
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(
        User,
        user_id
    )


def user_is_admin(user):
    """
    Prüft, ob der Benutzer der konfigurierte
    Administrator ist.
    """

    if not user:
        return False

    admin_username = current_app.config[
        "ADMIN_USERNAME"
    ]

    return (
        user.username.casefold()
        == admin_username.casefold()
    )
