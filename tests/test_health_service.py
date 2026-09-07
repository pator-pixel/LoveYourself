"""Tests für aktuelles Gewicht und Kalorienberechnung."""

from types import SimpleNamespace

from extensions import db
from models import Profile, WeightEntry
from services.health_service import calculate_calories, get_current_weight


def make_profile(**overrides):
    values = {
        "age": 30,
        "gender": "female",
        "height": 170,
        "weight": 80,
        "goal_weight": 70,
        "activity_level": "medium",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_calculate_calories_for_weight_loss():
    profile = make_profile()

    bmr, maintenance, target = calculate_calories(profile)

    expected_bmr = 1552
    expected_maintenance = int(expected_bmr * 1.55)
    expected_target = expected_maintenance - 500

    assert bmr == expected_bmr
    assert maintenance == expected_maintenance
    assert target == expected_target


def test_calculate_calories_uses_current_weight_when_supplied():
    profile = make_profile(weight=80)

    bmr_with_profile_weight, _, _ = calculate_calories(profile)
    bmr_with_current_weight, _, _ = calculate_calories(profile,current_weight=75,)

    assert bmr_with_profile_weight == 1552
    assert bmr_with_current_weight == 1502
    assert bmr_with_current_weight < bmr_with_profile_weight


def test_calorie_target_is_never_below_1200():
    profile = make_profile(age=80, height=140, weight=35, goal_weight=30, activity_level="low")

    _, _, target = calculate_calories(profile)

    assert target == 1200


def test_calculate_calories_returns_none_tuple_when_required_data_is_missing():
    profile = make_profile(age=None)

    assert calculate_calories(profile) == (None, None, None)
    assert calculate_calories(None) == (None, None, None)


def test_get_current_weight_prefers_latest_tracking_entry(app, user):
    with app.app_context():
        profile = Profile(user_id=user.id, weight=85)
        db.session.add(profile)
        db.session.add_all([
            WeightEntry(user_id=user.id, weight=83, date="2026-07-01"),
            WeightEntry(user_id=user.id, weight=81, date="2026-07-20"),
        ])
        db.session.commit()

        assert get_current_weight(user.id, profile) == 81


def test_get_current_weight_falls_back_to_profile_weight(app, user):
    with app.app_context():
        profile = Profile(user_id=user.id, weight=85)
        db.session.add(profile)
        db.session.commit()

        assert get_current_weight(user.id, profile) == 85
