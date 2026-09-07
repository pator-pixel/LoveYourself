import json
from datetime import date

from extensions import db
from models import (
    ExercisePreference,
    MealPreference,
    Plan,
    Profile,
)
from services.fitness_ai_service import generate_fitness_plan
from services.health_service import (
    calculate_calories,
    get_current_weight,
)
from services.nutrition_ai_service import generate_nutrition_plan
from services.plan_service import (
    build_fitness_prompt,
    build_nutrition_prompt,
    create_plan_titles,
)


class PlanGenerationError(RuntimeError):
    """Fehler bei der Erstellung eines AI-Plans."""


# =========================================================
# GEMEINSAME PROFILDATEN
# =========================================================

def _get_profile_and_weight(user):
    """
    Lädt das Profil und ermittelt das aktuelle Gewicht.
    """

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:
        raise ValueError("PROFILE_MISSING")

    current_weight = get_current_weight(
        user.id,
        profile
    )

    return profile, current_weight


# =========================================================
# GERICHTSBEWERTUNGEN
# =========================================================

def _get_meal_preferences(user_id):
    """
    Lädt die gespeicherten Gerichtspräferenzen
    eines Benutzers.

    like:
        Gericht darf bevorzugt wieder erscheinen.

    dislike:
        Gericht soll künftig ausgeschlossen werden.
    """

    preferences = (
        MealPreference.query
        .filter_by(
            user_id=user_id
        )
        .all()
    )

    liked_meals = []
    disliked_meals = []


    for preference in preferences:

        if preference.preference == "like":

            liked_meals.append(
                preference.meal_name
            )

        elif preference.preference == "dislike":

            disliked_meals.append(
                preference.meal_name
            )


    return (
        liked_meals,
        disliked_meals
    )


# =========================================================
# ÜBUNGSBEWERTUNGEN
# =========================================================

def _get_exercise_preferences(user_id):
    """
    Lädt die gespeicherten Übungspräferenzen
    eines Benutzers.

    like:
        Übung darf bevorzugt wieder erscheinen.

    dislike:
        Übung soll künftig ausgeschlossen werden.
    """

    preferences = (
        ExercisePreference.query
        .filter_by(
            user_id=user_id
        )
        .all()
    )

    liked_exercises = []
    disliked_exercises = []


    for preference in preferences:

        if preference.preference == "like":

            liked_exercises.append(
                preference.exercise_name
            )

        elif preference.preference == "dislike":

            disliked_exercises.append(
                preference.exercise_name
            )


    return (
        liked_exercises,
        disliked_exercises
    )


# =========================================================
# ERNÄHRUNGSPLAN + EINKAUFSLISTE
# =========================================================

def generate_and_save_nutrition_plan(user):
    """
    Erstellt ausschließlich einen Ernährungsplan
    inklusive der dazugehörigen Einkaufsliste.
    """

    profile, current_weight = _get_profile_and_weight(
        user
    )


    # -----------------------------------------------------
    # KALORIEN
    # -----------------------------------------------------

    (
        _,
        _,
        target_calories
    ) = calculate_calories(
        profile,
        current_weight
    )


    if target_calories is None:

        raise ValueError(
            "PROFILE_INCOMPLETE"
        )


    # -----------------------------------------------------
    # GERICHTSBEWERTUNGEN
    # -----------------------------------------------------

    (
        liked_meals,
        disliked_meals
    ) = _get_meal_preferences(
        user.id
    )


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    nutrition_prompt = build_nutrition_prompt(
        user,
        profile,
        current_weight,
        target_calories,
        liked_meals=liked_meals,
        disliked_meals=disliked_meals
    )


    # -----------------------------------------------------
    # AI-GENERIERUNG
    # -----------------------------------------------------

    try:

        nutrition_result = generate_nutrition_plan(
            nutrition_prompt
        )

    except Exception as error:

        raise PlanGenerationError(
            "Die Erstellung des Ernährungsplans "
            "ist fehlgeschlagen."
        ) from error


    # -----------------------------------------------------
    # ERGEBNIS AUSLESEN
    # -----------------------------------------------------

    nutrition_days = nutrition_result.get(
        "days",
        []
    )


    shopping_list = nutrition_result.get(
        "shopping_list",
        []
    )


    # -----------------------------------------------------
    # VALIDIERUNG
    # -----------------------------------------------------

    if len(nutrition_days) != 7:

        raise PlanGenerationError(
            "Der Ernährungsplan enthält nicht genau "
            "sieben Tage."
        )


    if not shopping_list:

        raise PlanGenerationError(
            "Die Einkaufsliste wurde nicht erstellt."
        )


    # -----------------------------------------------------
    # AUSGESCHLOSSENE GERICHTE PRÜFEN
    # -----------------------------------------------------

    disliked_normalized = {
        meal_name.strip().casefold()
        for meal_name in disliked_meals
        if meal_name.strip()
    }


    if disliked_normalized:

        for nutrition_day in nutrition_days:

            for meal_key in (
                "breakfast",
                "lunch",
                "snack",
                "dinner",
            ):

                meal = nutrition_day.get(
                    meal_key,
                    {}
                )


                meal_name = str(
                    meal.get(
                        "name",
                        ""
                    )
                ).strip()


                if (
                    meal_name.casefold()
                    in disliked_normalized
                ):

                    raise PlanGenerationError(
                        "Der Ernährungsplan enthält ein "
                        "Gericht, das von dir ausgeschlossen "
                        "wurde. Bitte erstelle den Plan erneut."
                    )


    # -----------------------------------------------------
    # TITEL
    # -----------------------------------------------------

    (
        nutrition_title,
        _,
        shopping_title
    ) = create_plan_titles(
        user.id
    )


    # -----------------------------------------------------
    # PLAN SPEICHERN
    # -----------------------------------------------------

    plan = Plan(

        plan_type="nutrition",

        nutrition_title=nutrition_title,

        shopping_title=shopping_title,

        created_at=date.today().isoformat(),

        current_weight=current_weight,

        calories=target_calories,

        allergies_snapshot=(
            profile.allergies
            or ""
        ),

        excluded_foods_snapshot=(
            profile.disliked_foods
            or ""
        ),

        nutrition_prompt=nutrition_prompt,

        nutrition_data=json.dumps(
            nutrition_days,
            ensure_ascii=False
        ),

        shopping_data=json.dumps(
            shopping_list,
            ensure_ascii=False
        ),

        user_id=user.id
    )


    db.session.add(
        plan
    )

    db.session.commit()

    return plan


# =========================================================
# FITNESSPLAN
# =========================================================

def generate_and_save_fitness_plan(user):
    """
    Erstellt ausschließlich einen Fitnessplan.
    """

    profile, current_weight = _get_profile_and_weight(
        user
    )


    # -----------------------------------------------------
    # TRAININGSTAGE
    # -----------------------------------------------------

    training_days = (
        profile.training_days
        or 1
    )


    # -----------------------------------------------------
    # ÜBUNGSBEWERTUNGEN
    # -----------------------------------------------------

    (
        liked_exercises,
        disliked_exercises
    ) = _get_exercise_preferences(
        user.id
    )


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    fitness_prompt = build_fitness_prompt(
        user,
        profile,
        current_weight,
        liked_exercises=liked_exercises,
        disliked_exercises=disliked_exercises
    )


    # -----------------------------------------------------
    # AI-GENERIERUNG
    # -----------------------------------------------------

    try:

        fitness_result = generate_fitness_plan(
            fitness_prompt,
            expected_training_days=training_days
        )

    except Exception as error:

        raise PlanGenerationError(
            "Die Erstellung des Fitnessplans "
            "ist fehlgeschlagen."
        ) from error


    # -----------------------------------------------------
    # ERGEBNIS AUSLESEN
    # -----------------------------------------------------

    fitness_days = fitness_result.get(
        "days",
        []
    )


    # -----------------------------------------------------
    # VALIDIERUNG
    # -----------------------------------------------------

    if len(fitness_days) != training_days:

        raise PlanGenerationError(
            "Der Fitnessplan enthält nicht die gewünschte "
            "Anzahl an Trainingstagen."
        )


    # -----------------------------------------------------
    # AUSGESCHLOSSENE ÜBUNGEN PRÜFEN
    # -----------------------------------------------------

    disliked_normalized = {
        exercise_name.strip().casefold()
        for exercise_name in disliked_exercises
        if exercise_name.strip()
    }


    if disliked_normalized:

        for fitness_day in fitness_days:

            exercises = fitness_day.get(
                "exercises",
                []
            )


            for exercise in exercises:

                exercise_name = str(
                    exercise.get(
                        "name",
                        ""
                    )
                ).strip()


                if (
                    exercise_name.casefold()
                    in disliked_normalized
                ):

                    raise PlanGenerationError(
                        "Der Fitnessplan enthält eine "
                        "Übung, die von dir ausgeschlossen "
                        "wurde. Bitte erstelle den Plan erneut."
                    )


    # -----------------------------------------------------
    # TITEL
    # -----------------------------------------------------

    (
        _,
        fitness_title,
        _
    ) = create_plan_titles(
        user.id
    )


    # -----------------------------------------------------
    # PLAN SPEICHERN
    # -----------------------------------------------------

    plan = Plan(

        plan_type="fitness",

        fitness_title=fitness_title,

        created_at=date.today().isoformat(),

        current_weight=current_weight,

        fitness_prompt=fitness_prompt,

        fitness_data=json.dumps(
            fitness_days,
            ensure_ascii=False
        ),

        user_id=user.id
    )


    db.session.add(
        plan
    )

    db.session.commit()

    return plan