from extensions import db
from models import Profile, WeightEntry


def get_current_weight(user_id, profile):
    """
    Gibt den neuesten Gewichtseintrag zurück.

    Wenn noch kein Tracking vorhanden ist,
    wird das Startgewicht aus dem Profil verwendet.
    """

    latest_entry = (
        WeightEntry.query
        .filter_by(user_id=user_id)
        .order_by(
            WeightEntry.date.desc(),
            WeightEntry.id.desc()
        )
        .first()
    )

    if latest_entry:
        return latest_entry.weight

    return (
        profile.weight
        if profile
        else None
    )


def calculate_calories(
    profile,
    current_weight=None
):
    """
    Berechnet:

    - Grundumsatz
    - Erhaltungsbedarf
    - tägliches Kalorienziel
    """

    if not profile:
        return None, None, None

    if (
        not profile.age
        or not profile.height
        or not profile.gender
    ):
        return None, None, None

    weight_for_calculation = (
        current_weight
        if current_weight is not None
        else profile.weight
    )

    if weight_for_calculation is None:
        return None, None, None

    if profile.gender == "male":
        bmr = (
            10 * weight_for_calculation
            + 6.25 * profile.height
            - 5 * profile.age
            + 5
        )

    else:
        bmr = (
            10 * weight_for_calculation
            + 6.25 * profile.height
            - 5 * profile.age
            - 161
        )

    activity_factors = {
        "low": 1.2,
        "medium": 1.55,
        "high": 1.75
    }

    activity_factor = activity_factors.get(
        profile.activity_level,
        1.2
    )

    maintenance_calories = round(
        bmr * activity_factor
    )

    if profile.goal_weight is None:
        target_calories = maintenance_calories

    elif profile.goal_weight < weight_for_calculation:
        target_calories = (
            maintenance_calories - 500
        )

    elif profile.goal_weight > weight_for_calculation:
        target_calories = (
            maintenance_calories + 300
        )

    else:
        target_calories = maintenance_calories

    target_calories = max(
        target_calories,
        1200
    )

    return (
        round(bmr),
        maintenance_calories,
        target_calories
    )
