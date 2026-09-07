from dataclasses import dataclass

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from extensions import db
from models import User
from utils.helpers import generate_temporary_password
from utils.validators import is_valid_password


class AccountValidationError(ValueError):
    """Fehlerhafte Eingabe bei Kontoaktionen."""


@dataclass
class RegistrationData:
    username: str
    password: str
    confirm_password: str
    language: str


def register_user(
    *,
    username,
    password,
    confirm_password,
    language="de",
):
    """Validiert die Registrierung und legt einen Benutzer an."""

    data = RegistrationData(
        username=username.strip(),
        password=password,
        confirm_password=confirm_password,
        language=language or "de",
    )

    if len(data.username) < 3:
        raise AccountValidationError(
            "Der Benutzername muss mindestens 3 Zeichen lang sein."
        )

    if User.query.filter_by(
        username=data.username
    ).first():
        raise AccountValidationError(
            "Dieser Benutzername ist bereits vergeben."
        )

    if data.password != data.confirm_password:
        raise AccountValidationError(
            "Die Passwörter stimmen nicht überein."
        )

    if not is_valid_password(data.password):
        raise AccountValidationError(
            "Das Passwort muss mindestens 8 Zeichen, "
            "einen Großbuchstaben, einen Kleinbuchstaben, "
            "eine Zahl und ein Sonderzeichen enthalten."
        )

    user = User(
        username=data.username,
        password_hash=generate_password_hash(
            data.password
        ),
        language=data.language
    )

    db.session.add(user)
    db.session.commit()

    return user


def authenticate_user(
    username,
    password,
):
    """Prüft Benutzername und Passwort."""

    user = User.query.filter_by(
        username=username.strip()
    ).first()

    if not user:
        return None

    if not check_password_hash(
        user.password_hash,
        password
    ):
        return None

    return user


def create_temporary_password(username):
    """
    Erzeugt und speichert ein temporäres Passwort.

    Gibt das temporäre Passwort zurück.
    """

    user = User.query.filter_by(
        username=username.strip()
    ).first()

    if not user:
        raise AccountValidationError(
            "Dieser Benutzername wurde nicht gefunden."
        )

    temporary_password = generate_temporary_password()

    user.password_hash = generate_password_hash(
        temporary_password
    )

    db.session.commit()

    return temporary_password


def update_password(
    *,
    user,
    current_password,
    new_password,
    confirm_password,
):
    """Validiert und speichert ein neues Passwort."""

    if not check_password_hash(
        user.password_hash,
        current_password
    ):
        raise AccountValidationError(
            "Das aktuelle Passwort ist falsch."
        )

    if new_password != confirm_password:
        raise AccountValidationError(
            "Die neuen Passwörter stimmen nicht überein."
        )

    if not is_valid_password(new_password):
        raise AccountValidationError(
            "Das neue Passwort erfüllt die "
            "Sicherheitsregeln nicht."
        )

    user.password_hash = generate_password_hash(
        new_password
    )

    db.session.commit()
