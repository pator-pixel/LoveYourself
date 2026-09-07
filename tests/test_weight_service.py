"""Tests für Umwandlung, Validierung und Datenbankzugriff beim Gewicht."""

import pytest

from extensions import db
from models import WeightEntry
from services.weight_service import (
    WeightValidationError,
    create_weight_entry,
    delete_weight_entry_for_user,
    get_weight_entries,
    parse_weight_value,
    validate_weight_value,
)


def test_parse_weight_value_converts_text_to_float():
    assert parse_weight_value(" 82.5 ") == 82.5


@pytest.mark.parametrize("value", ["", "abc", None])
def test_parse_weight_value_rejects_invalid_input(value):
    with pytest.raises(WeightValidationError, match="gültiges Gewicht"):
        parse_weight_value(value)


@pytest.mark.parametrize("value", [29.9, 300.1])
def test_validate_weight_value_rejects_values_outside_range(value):
    with pytest.raises(WeightValidationError, match="zwischen 30 und 300"):
        validate_weight_value(value)


@pytest.mark.parametrize("value", [30, 80.5, 300])
def test_validate_weight_value_accepts_valid_values(value):
    validate_weight_value(value)


def test_create_weight_entry_saves_entry(app, user):
    with app.app_context():
        entry = create_weight_entry(
            user_id=user.id,
            weight_text="81.7",
            entry_date="2026-07-26",
        )

        saved_entry = db.session.get(WeightEntry, entry.id)
        assert saved_entry.weight == 81.7
        assert saved_entry.date == "2026-07-26"
        assert saved_entry.user_id == user.id


def test_get_weight_entries_returns_newest_first(app, user):
    with app.app_context():
        create_weight_entry(user_id=user.id, weight_text="82", entry_date="2026-07-01")
        create_weight_entry(user_id=user.id, weight_text="81", entry_date="2026-07-20")

        entries = get_weight_entries(user.id)

        assert [entry.weight for entry in entries] == [81.0, 82.0]


def test_user_cannot_delete_another_users_entry(app, user):
    with app.app_context():
        entry = create_weight_entry(
            user_id=user.id,
            weight_text="80",
            entry_date="2026-07-26",
        )

        deleted = delete_weight_entry_for_user(entry_id=entry.id, user_id=9999)

        assert deleted is False
        assert db.session.get(WeightEntry, entry.id) is not None
