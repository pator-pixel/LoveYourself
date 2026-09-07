from schemas.fitness import FitnessPlanResult
from services.ai_instructions import FITNESS_INSTRUCTIONS
from services.openai_client import client


def _validate_fitness_result(
    result: FitnessPlanResult,
    expected_training_days: int
) -> FitnessPlanResult:
    if len(result.days) != expected_training_days:
        raise RuntimeError(
            "Die AI hat nicht die gewünschte Anzahl "
            "an Trainingstagen erstellt."
        )

    expected_days = list(
        range(1, expected_training_days + 1)
    )

    received_days = sorted(
        fitness_day.day
        for fitness_day in result.days
    )

    if received_days != expected_days:
        raise RuntimeError(
            "Die Trainingstage müssen mit Tag 1 beginnen "
            "und fortlaufend nummeriert sein."
        )

    return result


def generate_fitness_plan(
    prompt: str,
    expected_training_days: int
) -> dict:
    """Erstellt einen strukturierten Fitnessplan."""

    if not prompt or not prompt.strip():
        raise ValueError(
            "Der Fitness-Prompt darf nicht leer sein."
        )

    if not 1 <= expected_training_days <= 7:
        raise ValueError(
            "Die Trainingstage müssen zwischen 1 und 7 liegen."
        )

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": FITNESS_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=FitnessPlanResult
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "Die AI hat keinen gültigen Fitnessplan geliefert."
        )

    validated_result = _validate_fitness_result(
        result,
        expected_training_days
    )

    return validated_result.model_dump()
