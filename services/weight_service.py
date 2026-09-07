from datetime import date

from extensions import db
from models import WeightEntry


class WeightValidationError(ValueError):
    """Fehlerhafte Gewichtseingabe."""


def parse_weight_value(weight_text):
    """Wandelt eine Gewichtseingabe in float um."""

    try:
        return float(
            weight_text.strip()
        )

    except (
        AttributeError,
        ValueError
    ) as error:
        raise WeightValidationError(
            "Bitte gib ein gültiges Gewicht ein."
        ) from error


def validate_weight_value(weight_value):
    """Prüft einen realistischen Gewichtsbereich."""

    if not 30 <= weight_value <= 300:
        raise WeightValidationError(
            "Bitte gib ein realistisches Gewicht "
            "zwischen 30 und 300 kg ein."
        )


def parse_entry_date(entry_date):
    """
    Wandelt das eingegebene Datum in ein date-Objekt um.
    Wenn kein Datum angegeben wurde, wird heute verwendet.
    """

    if not entry_date:
        return date.today()

    try:
        return date.fromisoformat(
            entry_date.strip()
        )

    except (
        AttributeError,
        ValueError
    ) as error:
        raise WeightValidationError(
            "Bitte gib ein gültiges Datum ein."
        ) from error


def validate_entry_date(entry_date_value):
    """
    Verhindert Gewichtseinträge in der Zukunft.
    Erlaubt sind nur heute und vergangene Tage.
    """

    if entry_date_value > date.today():
        raise WeightValidationError(
            "Ein Gewichtseintrag kann nicht "
            "in der Zukunft liegen."
        )


def create_weight_entry(
    *,
    user_id,
    weight_text,
    entry_date="",
):
    """Validiert und speichert einen Gewichtseintrag."""

    # =====================================================
    # GEWICHT
    # =====================================================

    weight_value = parse_weight_value(
        weight_text
    )

    validate_weight_value(
        weight_value
    )


    # =====================================================
    # DATUM
    # =====================================================

    entry_date_value = parse_entry_date(
        entry_date
    )

    validate_entry_date(
        entry_date_value
    )


    # =====================================================
    # SPEICHERN
    # =====================================================

    weight_entry = WeightEntry(
        weight=weight_value,
        date=entry_date_value.isoformat(),
        user_id=user_id
    )

    db.session.add(weight_entry)
    db.session.commit()

    return weight_entry


def get_weight_entries(user_id):
    """Lädt alle Gewichtseinträge, neueste zuerst."""

    return (
        WeightEntry.query
        .filter_by(user_id=user_id)
        .order_by(
            WeightEntry.date.desc(),
            WeightEntry.id.desc()
        )
        .all()
    )


def delete_weight_entry_for_user(
    *,
    entry_id,
    user_id,
):
    """
    Löscht einen Gewichtseintrag nur dann,
    wenn er dem Benutzer gehört.
    """

    weight_entry = WeightEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()

    if not weight_entry:
        return False

    db.session.delete(weight_entry)
    db.session.commit()

    return True