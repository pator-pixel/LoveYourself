"""Unit-Tests der KI-Ergebnisprüfung – ohne echten API-Aufruf."""

import pytest

from schemas.fitness import Exercise, FitnessDay, FitnessPlanResult
from schemas.nutrition import Meal, NutritionDay, NutritionPlanResult, ShoppingCategory
from services.fitness_ai_service import _validate_fitness_result
from services.nutrition_ai_service import _validate_nutrition_result


def meal(name="Gericht", calories=400):
    return Meal(name=name, calories=calories)


def nutrition_day(day):
    return NutritionDay(
        day=day,
        breakfast=meal("Frühstück"),
        lunch=meal("Mittagessen"),
        dinner=meal("Abendessen"),
        snack=meal("Snack", 150),
    )


def test_nutrition_validation_accepts_seven_numbered_days_and_shopping_list():
    result = NutritionPlanResult(
        days=[nutrition_day(day) for day in range(1, 8)],
        shopping_list=[ShoppingCategory(category="Gemüse", items=["Paprika"])],
    )

    assert _validate_nutrition_result(result) is result


def test_nutrition_validation_rejects_missing_day():
    # model_construct umgeht hier bewusst Pydantics erste Schutzschicht,
    # damit wir die zusätzliche Service-Prüfung isoliert testen können.
    result = NutritionPlanResult.model_construct(
        days=[nutrition_day(day) for day in range(1, 7)],
        shopping_list=[ShoppingCategory(category="Gemüse", items=["Paprika"])],
    )

    with pytest.raises(RuntimeError, match="sieben"):
        _validate_nutrition_result(result)


def test_nutrition_validation_rejects_empty_shopping_list():
    result = NutritionPlanResult(
        days=[nutrition_day(day) for day in range(1, 8)],
        shopping_list=[],
    )

    with pytest.raises(RuntimeError, match="Einkaufsliste"):
        _validate_nutrition_result(result)


def exercise(name):
    return Exercise(
        name=name,
        sets="3",
        repetitions="10",
        pause="60 Sekunden",
        alternative="Leichtere Variante",
    )


def fitness_day(day):
    return FitnessDay(
        day=day,
        exercises=[
            exercise("Kniebeuge"),
            exercise("Wandliegestütz"),
            exercise("Glute Bridge"),
        ],
        steps_alternative="8.000 Schritte",
    )


def test_fitness_validation_accepts_expected_training_days():
    result = FitnessPlanResult(days=[fitness_day(1), fitness_day(2), fitness_day(3)])

    assert _validate_fitness_result(result, 3) is result


def test_fitness_validation_rejects_wrong_numbering():
    result = FitnessPlanResult(days=[fitness_day(1), fitness_day(3)])

    with pytest.raises(RuntimeError, match="fortlaufend"):
        _validate_fitness_result(result, 2)
