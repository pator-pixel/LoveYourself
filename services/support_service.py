from extensions import db
from models import SupportMessage
from utils.constants import (
    SUPPORT_CATEGORIES,
    SUPPORT_STATUS_VALUES,
)


class SupportValidationError(ValueError):
    """Fehlerhafte Eingabe im Supportbereich."""


def create_support_message(
    *,
    user,
    subject,
    category,
    message_text,
):
    """Validiert und speichert eine Supportanfrage."""

    subject = subject.strip()
    category = category.strip()
    message_text = message_text.strip()

    if len(subject) < 3:
        raise SupportValidationError(
            "Bitte gib einen aussagekräftigen "
            "Betreff ein."
        )

    if len(subject) > 180:
        raise SupportValidationError(
            "Der Betreff darf höchstens "
            "180 Zeichen lang sein."
        )

    if category not in SUPPORT_CATEGORIES:
        raise SupportValidationError(
            "Bitte wähle eine gültige Kategorie."
        )

    if len(message_text) < 10:
        raise SupportValidationError(
            "Bitte beschreibe dein Anliegen "
            "mit mindestens 10 Zeichen."
        )

    if len(message_text) > 5000:
        raise SupportValidationError(
            "Die Nachricht darf höchstens "
            "5.000 Zeichen lang sein."
        )

    support_message = SupportMessage(
        subject=subject,
        category=category,
        message=message_text,
        status="Offen",
        user_id=user.id
    )

    db.session.add(support_message)
    db.session.commit()

    return support_message


def get_user_support_messages(user_id):
    """Lädt die Supportanfragen eines Benutzers."""

    return (
        SupportMessage.query
        .filter_by(user_id=user_id)
        .order_by(
            SupportMessage.created_at.desc()
        )
        .all()
    )


def update_support_message(
    *,
    message_id,
    new_status,
    admin_response,
):
    """Validiert und aktualisiert eine Supportanfrage."""

    support_message = db.session.get(
        SupportMessage,
        message_id
    )

    if not support_message:
        raise SupportValidationError(
            "Die Supportnachricht wurde "
            "nicht gefunden."
        )

    if new_status not in SUPPORT_STATUS_VALUES:
        raise SupportValidationError(
            "Bitte wähle einen gültigen Status."
        )

    admin_response = admin_response.strip()

    if len(admin_response) > 5000:
        raise SupportValidationError(
            "Die Antwort darf höchstens "
            "5.000 Zeichen lang sein."
        )

    support_message.status = new_status
    support_message.admin_response = (
        admin_response or None
    )

    if (
        admin_response
        and new_status != "Geschlossen"
    ):
        support_message.status = "Beantwortet"

    db.session.commit()

    return support_message


def get_support_overview(selected_status=""):
    """
    Liefert Supportnachrichten und Statuszählungen
    für den Adminbereich.
    """

    selected_status = selected_status.strip()

    query = SupportMessage.query

    if selected_status in SUPPORT_STATUS_VALUES:
        query = query.filter_by(
            status=selected_status
        )

    support_messages = (
        query
        .order_by(
            SupportMessage.created_at.desc()
        )
        .all()
    )

    status_counts = {
        status: SupportMessage.query.filter_by(
            status=status
        ).count()
        for status in SUPPORT_STATUS_VALUES
    }

    return {
        "support_messages": support_messages,
        "status_values": SUPPORT_STATUS_VALUES,
        "status_counts": status_counts,
        "selected_status": selected_status,
    }
