"""Unit-Tests für das Lesen und Prüfen der Profilwerte."""

import pytest

from services.profile_service import (
    ProfileValidationError,
    ProfileValues,
    parse_profile_values,
    validate_profile_values,
)


class DummyForm:
    """Kleine Formularattrappe mit der für den Test benötigten get-Methode."""

    def __init__(self, values=None):
        self.values = values or {}

    def get(self, key, default=""):
        return self.values.get(key, default)


def test_parse_profile_values_converts_text_to_numbers():
    form = DummyForm({
        "age": "29",
        "height": "168.5",
        "weight": "82.4",
        "goal_weight": "70",
        "training_days": "3",
    })

    values = parse_profile_values(form)

    assert values == ProfileValues(
        age=29,
        height=168.5,
        start_weight=82.4,
        goal_weight=70.0,
        training_days=3,
    )


def test_parse_profile_values_turns_empty_fields_into_none():
    values = parse_profile_values(DummyForm())

    assert values == ProfileValues(None, None, None, None, None)


def test_parse_profile_values_rejects_non_numeric_input():
    form = DummyForm({"age": "neunundzwanzig"})

    with pytest.raises(ProfileValidationError, match="Zahlenangaben"):
        parse_profile_values(form)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (ProfileValues(15, 170, 80, 70, 3), "Alter"),
        (ProfileValues(25, 99, 80, 70, 3), "Größe"),
        (ProfileValues(25, 170, 29, 70, 3), "Startgewicht"),
        (ProfileValues(25, 170, 80, 301, 3), "Zielgewicht"),
        (ProfileValues(25, 170, 80, 70, 0), "Trainingstage"),
    ],
)
def test_validate_profile_values_rejects_unrealistic_values(values, message):
    with pytest.raises(ProfileValidationError, match=message):
        validate_profile_values(values)


def test_validate_profile_values_accepts_boundary_values():
    values = ProfileValues(
        age=16,
        height=100,
        start_weight=30,
        goal_weight=300,
        training_days=7,
    )

    validate_profile_values(values)
