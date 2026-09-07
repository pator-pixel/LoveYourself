"""Unit-Tests für die allgemeinen Eingabeprüfungen."""

import pytest

from utils.validators import is_valid_password


@pytest.mark.parametrize("password", [
    "Sicher123!",
    "NochBesser9#",
    "A1b!xxxx",
])
def test_valid_password_is_accepted(password):
    assert is_valid_password(password) is True


@pytest.mark.parametrize("password", [
    "",
    None,
    "Kurz1!",
    "nurklein1!",
    "NUR-GROSS1!",
    "KeineZahl!",
    "KeinSonderzeichen1",
])
def test_invalid_password_is_rejected(password):
    assert is_valid_password(password) is False
