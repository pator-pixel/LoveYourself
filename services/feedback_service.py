from datetime import date

from extensions import db
from models import PlanFeedback
from utils.helpers import merge_lines


def _remove_lines(existing_value, value_to_remove):
    """Entfernt frühere Feedback-Werte aus einem zeilenweisen Profilfeld."""

    if not existing_value:
        return ""

    remove_items = {
        item.strip().casefold()
        for item in (value_to_remove or "").splitlines()
        if item.strip()
    }

    if not remove_items:
        return existing_value

    remaining_items = [
        item.strip()
        for item in existing_value.splitlines()
        if item.strip() and item.strip().casefold() not in remove_items
    ]

    return "\n".join(remaining_items)


def _remove_old_feedback_from_profile(profile, feedback):
    """Nimmt die Werte des alten Feedbacks zurück, bevor es geändert wird."""

    if not feedback:
        return

    if feedback.feedback_type == "nutrition":
        profile.liked_foods = _remove_lines(
            profile.liked_foods, feedback.liked_items
        )
        profile.disliked_foods = _remove_lines(
            profile.disliked_foods, feedback.disliked_items
        )
        profile.favorite_meals = _remove_lines(
            profile.favorite_meals, feedback.favorite_meals
        )
        profile.nutrition_wishes = _remove_lines(
            profile.nutrition_wishes, feedback.selected_preferences
        )
        profile.nutrition_wishes = _remove_lines(
            profile.nutrition_wishes, feedback.wishes
        )
    else:
        profile.liked_exercises = _remove_lines(
            profile.liked_exercises, feedback.liked_items
        )
        profile.disliked_exercises = _remove_lines(
            profile.disliked_exercises, feedback.disliked_items
        )
        profile.preferred_training_types = _remove_lines(
            profile.preferred_training_types, feedback.selected_preferences
        )
        profile.fitness_wishes = _remove_lines(
            profile.fitness_wishes, feedback.wishes
        )

        if (
            feedback.preferred_training_duration
            and profile.preferred_training_duration
            == feedback.preferred_training_duration
        ):
            profile.preferred_training_duration = None


def save_plan_feedback(
    *,
    user,
    plan,
    profile,
    feedback_type,
    rating,
    liked_items,
    disliked_items,
    favorite_meals,
    selected_preferences,
    preferred_training_duration,
    wishes,
    comment,
    existing_feedback=None,
):
    """Erstellt Feedback oder aktualisiert das vorhandene Feedback eines Plans."""

    if existing_feedback:
        feedback = existing_feedback
        _remove_old_feedback_from_profile(profile, feedback)
    else:
        feedback = PlanFeedback(
            feedback_type=feedback_type,
            plan_id=plan.id,
            user_id=user.id,
            created_at=date.today().isoformat(),
        )
        db.session.add(feedback)

    feedback.feedback_type = feedback_type
    feedback.rating = rating
    feedback.liked_items = liked_items
    feedback.disliked_items = disliked_items
    feedback.favorite_meals = favorite_meals
    feedback.selected_preferences = selected_preferences
    feedback.preferred_training_duration = (
        preferred_training_duration or None
    )
    feedback.preferred_training_time = None
    feedback.wishes = wishes
    feedback.comment = comment
    feedback.created_at = date.today().isoformat()

    if feedback_type == "nutrition":
        profile.liked_foods = merge_lines(profile.liked_foods, liked_items)
        profile.disliked_foods = merge_lines(profile.disliked_foods, disliked_items)
        profile.favorite_meals = merge_lines(profile.favorite_meals, favorite_meals)
        profile.nutrition_wishes = merge_lines(
            profile.nutrition_wishes, selected_preferences
        )
        profile.nutrition_wishes = merge_lines(profile.nutrition_wishes, wishes)
    else:
        profile.liked_exercises = merge_lines(profile.liked_exercises, liked_items)
        profile.disliked_exercises = merge_lines(
            profile.disliked_exercises, disliked_items
        )
        profile.preferred_training_types = merge_lines(
            profile.preferred_training_types, selected_preferences
        )

        if preferred_training_duration:
            profile.preferred_training_duration = preferred_training_duration

        profile.fitness_wishes = merge_lines(profile.fitness_wishes, wishes)

    # Falls es aus älteren Versionen mehrere Feedback-Einträge für denselben
    # Plan gibt, bleibt ab jetzt nur der aktuell bearbeitete Eintrag bestehen.
    duplicates = (
        PlanFeedback.query
        .filter_by(
            user_id=user.id,
            plan_id=plan.id,
            feedback_type=feedback_type,
        )
        .all()
    )

    for duplicate in duplicates:
        if duplicate.id != feedback.id:
            db.session.delete(duplicate)

    db.session.commit()
    return feedback
