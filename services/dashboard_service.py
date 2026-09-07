from models import Profile, WeightEntry
from services.health_service import (
    calculate_calories,
    get_current_weight,
)


def _calculate_remaining_weight(
    *,
    start_weight,
    current_weight,
    goal_weight,
):
    if (
        start_weight is None
        or current_weight is None
        or goal_weight is None
    ):
        return None

    if goal_weight < start_weight:
        return max(
            round(
                current_weight - goal_weight,
                1
            ),
            0
        )

    if goal_weight > start_weight:
        return max(
            round(
                goal_weight - current_weight,
                1
            ),
            0
        )

    return 0


def _build_weight_change_text(
    *,
    start_weight,
    current_weight,
):
    if (
        start_weight is None
        or current_weight is None
    ):
        return None

    difference = round(
        current_weight - start_weight,
        1
    )

    if difference < 0:
        return (
            f"{abs(difference)} kg abgenommen"
        )

    if difference > 0:
        return (
            f"{difference} kg zugenommen"
        )

    return "Keine Veränderung"


def _calculate_progress_percent(
    *,
    start_weight,
    current_weight,
    goal_weight,
):
    if (
        start_weight is None
        or current_weight is None
        or goal_weight is None
    ):
        return None

    if goal_weight < start_weight:
        total_goal = (
            start_weight - goal_weight
        )

        current_progress = (
            start_weight - current_weight
        )

    elif goal_weight > start_weight:
        total_goal = (
            goal_weight - start_weight
        )

        current_progress = (
            current_weight - start_weight
        )

    else:
        return 100

    if total_goal <= 0:
        return None

    progress_percent = round(
        current_progress
        / total_goal
        * 100
    )

    return max(
        0,
        min(
            progress_percent,
            100
        )
    )


def build_dashboard_data(user):
    """
    Lädt und berechnet alle Daten für das Dashboard.
    """

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    entries = (
        WeightEntry.query
        .filter_by(user_id=user.id)
        .order_by(
            WeightEntry.date.asc(),
            WeightEntry.id.asc()
        )
        .all()
    )

    start_weight = (
        profile.weight
        if profile
        else None
    )

    goal_weight = (
        profile.goal_weight
        if profile
        else None
    )

    current_weight = get_current_weight(
        user.id,
        profile
    )

    (
        bmr,
        maintenance_calories,
        target_calories
    ) = calculate_calories(
        profile,
        current_weight
    )

    return {
        "user": user,
        "current_weight": current_weight,
        "goal_weight": goal_weight,
        "remaining_weight": _calculate_remaining_weight(
            start_weight=start_weight,
            current_weight=current_weight,
            goal_weight=goal_weight,
        ),
        "start_weight": start_weight,
        "weight_change_text": _build_weight_change_text(
            start_weight=start_weight,
            current_weight=current_weight,
        ),
        "progress_percent": _calculate_progress_percent(
            start_weight=start_weight,
            current_weight=current_weight,
            goal_weight=goal_weight,
        ),
        "total_entries": len(entries),
        "bmr": bmr,
        "maintenance_calories": maintenance_calories,
        "target_calories": target_calories,
    }
