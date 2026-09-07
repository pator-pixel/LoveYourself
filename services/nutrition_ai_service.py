from schemas.nutrition import NutritionPlanResult
from services.ai_instructions import NUTRITION_INSTRUCTIONS
from services.openai_client import client


def _validate_nutrition_result(
    result: NutritionPlanResult
) -> NutritionPlanResult:
    if len(result.days) != 7:
        raise RuntimeError(
            "Die AI hat nicht genau sieben Ernährungstage erstellt."
        )

    expected_days = list(range(1, 8))
    received_days = sorted(
        nutrition_day.day
        for nutrition_day in result.days
    )

    if received_days != expected_days:
        raise RuntimeError(
            "Die Ernährungstage müssen von Tag 1 bis Tag 7 reichen."
        )

    if not result.shopping_list:
        raise RuntimeError(
            "Die AI hat keine Einkaufsliste erstellt."
        )

    return result


def generate_nutrition_plan(prompt: str) -> dict:
    """
    Erstellt einen strukturierten Ernährungsplan
    inklusive Einkaufsliste.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Der Ernährungs-Prompt darf nicht leer sein."
        )

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": NUTRITION_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=NutritionPlanResult
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "Die AI hat keinen gültigen Ernährungsplan geliefert."
        )

    validated_result = _validate_nutrition_result(
        result
    )

    return validated_result.model_dump()
