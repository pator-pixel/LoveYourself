from dataclasses import dataclass

from extensions import db
from models import Profile


@dataclass
class ProfileValues:
    age: int | None
    height: float | None
    start_weight: float | None
    goal_weight: float | None
    training_days: int | None


class ProfileValidationError(ValueError):
    """Fehlerhafte oder unrealistische Profilangabe."""


def _optional_int(
    form,
    field_name
):
    value = form.get(
        field_name,
        ""
    ).strip()

    return int(value) if value else None


def _optional_float(
    form,
    field_name
):
    value = form.get(
        field_name,
        ""
    ).strip()

    return float(value) if value else None


def parse_profile_values(form):
    """
    Liest die numerischen Formularwerte ein
    und wandelt sie in passende Python-Typen um.
    """

    try:
        return ProfileValues(
            age=_optional_int(
                form,
                "age"
            ),
            height=_optional_float(
                form,
                "height"
            ),
            start_weight=_optional_float(
                form,
                "weight"
            ),
            goal_weight=_optional_float(
                form,
                "goal_weight"
            ),
            training_days=_optional_int(
                form,
                "training_days"
            ),
        )

    except ValueError as error:
        raise ProfileValidationError(
            "Bitte überprüfe deine Zahlenangaben."
        ) from error


def validate_profile_values(values):
    """Prüft die erlaubten Wertebereiche."""

    if (
        values.age is not None
        and not 16 <= values.age <= 120
    ):
        raise ProfileValidationError(
            "Das Alter muss zwischen 16 und 120 liegen."
        )

    if (
        values.height is not None
        and not 100 <= values.height <= 250
    ):
        raise ProfileValidationError(
            "Die Größe muss zwischen 100 und 250 cm liegen."
        )

    if (
        values.start_weight is not None
        and not 30 <= values.start_weight <= 300
    ):
        raise ProfileValidationError(
            "Das Startgewicht muss zwischen 30 und 300 kg liegen."
        )

    if (
        values.goal_weight is not None
        and not 30 <= values.goal_weight <= 300
    ):
        raise ProfileValidationError(
            "Das Zielgewicht muss zwischen 30 und 300 kg liegen."
        )

    if (
        values.training_days is not None
        and not 1 <= values.training_days <= 7
    ):
        raise ProfileValidationError(
            "Trainingstage müssen zwischen 1 und 7 liegen."
        )


def _form_list(
    form,
    field_name
):
    return "\n".join(
        item.strip()
        for item in form.getlist(field_name)
        if item.strip()
    )


def _combine_choice_fields(
    form,
    checkbox_field,
    custom_field
):
    selected_values = [
        value.strip()
        for value in form.getlist(
            checkbox_field
        )
        if value.strip()
    ]

    custom_value = form.get(
        custom_field,
        ""
    ).strip()

    if custom_value:
        known_values = {
            value.casefold()
            for value in selected_values
        }

        for item in custom_value.splitlines():
            item = item.strip()

            if (
                item
                and item.casefold() not in known_values
            ):
                selected_values.append(item)
                known_values.add(
                    item.casefold()
                )

    return "\n".join(selected_values)


def save_profile_from_form(
    user,
    form
):
    """
    Validiert das Formular und speichert das Profil.

    Gibt das gespeicherte Profil zurück.
    """

    values = parse_profile_values(form)
    validate_profile_values(values)

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if profile is None:
        profile = Profile(
            user_id=user.id
        )

        db.session.add(profile)

    profile.age = values.age
    profile.gender = form.get("gender")
    profile.height = values.height
    profile.weight = values.start_weight
    profile.goal_weight = values.goal_weight

    profile.activity_level = form.get(
        "activity_level"
    )

    profile.diet_type = form.get(
        "diet_type"
    )

    profile.allergies = _form_list(
        form,
        "allergies_item"
    )

    profile.diseases = _form_list(
        form,
        "diseases_item"
    )

    profile.limitations = _form_list(
        form,
        "limitations_item"
    )

    profile.liked_foods = _form_list(
        form,
        "liked_foods_item"
    )

    profile.disliked_foods = _form_list(
        form,
        "disliked_foods_item"
    )

    profile.favorite_meals = _form_list(
        form,
        "favorite_meals_item"
    )

    profile.nutrition_wishes = (
        _combine_choice_fields(
            form,
            "nutrition_wishes_choices",
            "nutrition_wishes_other"
        )
    )

    profile.fitness_level = form.get(
        "fitness_level"
    )

    profile.training_days = values.training_days

    profile.has_gym = (
        form.get("has_gym") == "yes"
    )

    profile.home_equipment = _form_list(
        form,
        "home_equipment_item"
    )

    profile.liked_exercises = _form_list(
        form,
        "liked_exercises_item"
    )

    profile.disliked_exercises = _form_list(
        form,
        "disliked_exercises_item"
    )

    profile.preferred_training_types = (
        _combine_choice_fields(
            form,
            "preferred_training_types_choices",
            "preferred_training_types_other"
        )
    )

    profile.preferred_training_duration = (
        form.get(
            "preferred_training_duration",
            ""
        ).strip()
        or None
    )

    profile.fitness_wishes = (
        _combine_choice_fields(
            form,
            "fitness_wishes_choices",
            "fitness_wishes_other"
        )
    )

    # Nicht mehr genutzte Felder leeren.
    profile.preferred_training_time = None
    profile.nutrition_notes = None
    profile.fitness_notes = None

    db.session.commit()

    return profile
