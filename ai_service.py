import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY wurde nicht gefunden. "
        "Prüfe deine .env-Datei."
    )


client = OpenAI(
    api_key=OPENAI_API_KEY
)


# -------------------------------------------------------------------
# Struktur des Ernährungsplans
# -------------------------------------------------------------------

class Meal(BaseModel):
    name: str = Field(
        description=(
            "Kurzer Name der Mahlzeit, ohne langen Erklärungstext."
        )
    )

    calories: int = Field(
        ge=0,
        description="Ungefähre Kalorienzahl der Mahlzeit."
    )


class NutritionDay(BaseModel):
    day: int = Field(
        ge=1,
        le=7,
        description="Tag als Zahl zwischen 1 und 7."
    )

    breakfast: Meal
    lunch: Meal
    dinner: Meal
    snack: Meal


class ShoppingCategory(BaseModel):
    category: str = Field(
        description=(
            "Kurzer Kategoriename, zum Beispiel Gemüse, Obst "
            "oder Proteinquellen."
        )
    )

    items: List[str] = Field(
        description=(
            "Kurze, eindeutige Zutaten. Keine Erklärungen "
            "und keine doppelten Zutaten."
        )
    )


class NutritionPlanResult(BaseModel):
    days: List[NutritionDay] = Field(
        min_length=7,
        max_length=7,
        description="Genau sieben Ernährungstage."
    )

    shopping_list: List[ShoppingCategory] = Field(
        description=(
            "Kompakte Einkaufsliste, nach sinnvollen "
            "Kategorien sortiert."
        )
    )


# -------------------------------------------------------------------
# Struktur des Fitnessplans
# -------------------------------------------------------------------

class Exercise(BaseModel):
    name: str = Field(
        description="Kurzer Name der Übung."
    )

    sets: str = Field(
        description=(
            "Anzahl der Sätze, zum Beispiel 3."
        )
    )

    repetitions: str = Field(
        description=(
            "Wiederholungen oder Zeit, zum Beispiel 10 bis 12 "
            "oder 30 Sekunden."
        )
    )

    pause: str = Field(
        description=(
            "Kurze Pausenangabe, zum Beispiel 60 Sekunden."
        )
    )

    alternative: str = Field(
        description=(
            "Eine kurze, einfachere Alternative. "
            "Keine längere Erklärung."
        )
    )


class FitnessDay(BaseModel):
    day: int = Field(
        ge=1,
        description="Trainingstag als Zahl: Tag 1, Tag 2 und so weiter."
    )

    exercises: List[Exercise] = Field(
        min_length=3,
        description=(
            "Eine kurze, übersichtliche Übungsliste."
        )
    )

    steps_alternative: str = Field(
        description=(
            "Kurzes Schritte-Ziel für den Fall, dass die "
            "Trainingseinheit nicht durchgeführt wird."
        )
    )


class FitnessPlanResult(BaseModel):
    days: List[FitnessDay] = Field(
        min_length=1,
        max_length=7,
        description=(
            "Genau so viele Trainingstage, wie im Profil angegeben."
        )
    )


# -------------------------------------------------------------------
# Allgemeine Hinweise für die AI
# -------------------------------------------------------------------

GENERAL_INSTRUCTIONS = """
Du arbeitest für die App "Love Yourself".

Die Pläne sollen motivierend, leicht verständlich und sehr übersichtlich
sein. Vermeide lange Einleitungen, Abschlussformulierungen,
Wiederholungen und unnötige Erklärungen.

Verbindliche Regeln:

- Antworte vollständig auf Deutsch.
- Gib keine medizinischen Diagnosen.
- Gib keine Heilversprechen.
- Empfehle keine extreme Diät.
- Empfehle keine gefährlichen Trainingsmethoden.
- Erfinde keine Angaben, die nicht im Prompt stehen.
- Füge keinen Satz wie "Wenn du möchtest, kann ich ..." hinzu.
- Füge keine zusätzlichen Kapitel oder freien Text außerhalb
  der vorgegebenen Datenstruktur hinzu.
"""


NUTRITION_INSTRUCTIONS = (
    GENERAL_INSTRUCTIONS
    + """
Du erstellst ausschließlich:

1. einen kompakten 7-Tage-Ernährungsplan
2. eine kurze, sortierte Einkaufsliste

Der Ernährungsplan wird später als Tabelle dargestellt.

Deshalb müssen die Mahlzeitennamen kurz bleiben.

Gute Beispiele:

- Haferflocken mit Beeren
- Hähnchen-Reis-Bowl
- Lachs mit Kartoffeln
- Joghurt mit Apfel

Schlechte Beispiele:

- Bereite zunächst die Haferflocken zu und füge danach ...
- Dieses gesunde und ausgewogene Frühstück enthält ...

Weitere Regeln:

- Erstelle genau sieben Tage.
- Benenne die Tage nur mit den Zahlen 1 bis 7.
- Jeder Tag enthält Frühstück, Mittagessen, Abendessen und Snack.
- Jede Mahlzeit enthält nur einen kurzen Namen und ungefähre Kalorien.
- Die Summe eines Tages soll ungefähr dem Kalorienziel entsprechen.
- Allergien sind absolute Ausschlusskriterien.
- Ausgeschlossene Lebensmittel dürfen nicht vorkommen.
- Berücksichtige auch verwandte Formen allergischer Zutaten.

Beispiel:
Wenn Zwiebeln ausgeschlossen sind, sind auch Schalotten,
Frühlingszwiebeln, Röstzwiebeln, Zwiebelpulver und
zwiebelhaltige Fertigsoßen ausgeschlossen.

Einkaufsliste:

- Verwende kurze Zutatenbezeichnungen.
- Führe identische Zutaten nur einmal auf.
- Verwende höchstens sinnvolle, notwendige Kategorien.
- Füge keine Kochanleitungen hinzu.
- Füge keine Einleitung oder Schlussbemerkung hinzu.
"""
)


FITNESS_INSTRUCTIONS = (
    GENERAL_INSTRUCTIONS
    + """
Du erstellst ausschließlich einen einfachen Trainingsplan.

Der Plan wird später als Tabelle dargestellt.

Die Antwort darf nicht enthalten:

- Trainingsziel als eigenes Kapitel
- verfügbare Trainingsmöglichkeiten als eigenes Kapitel
- ausführliche Profildaten
- Regeneration und Hinweise als eigenes Kapitel
- lange Übungserklärungen
- feste Wochentage
- Tageszeiten
- Tag A, Tag B oder Tag C

Weitere Regeln:

- Benenne Trainingstage nur als Tag 1, Tag 2, Tag 3 und so weiter.
- Erstelle genau so viele Trainingstage, wie im Prompt angegeben.
- Jede Übung enthält nur:
  Name, Sätze, Wiederholungen oder Dauer, Pause und Alternative.
- Halte die Zahl der Übungen übersichtlich.
- Verwende bevorzugte Trainingsarten und beliebte Übungen.
- Verwende keine unbeliebten Übungen.
- Berücksichtige körperliche Einschränkungen.
- Berücksichtige die gewünschte Trainingsdauer.
- Wenn kein Fitnessstudio vorhanden ist, verwende ausschließlich
  Körpergewicht und das angegebene Home-Equipment.
- Wenn ein Fitnessstudio vorhanden ist, dürfen passende Geräte
  und freie Gewichte verwendet werden.
- Füge pro Trainingstag nur eine kurze Schritte-Alternative hinzu.
- Füge keine Einleitung oder Schlussbemerkung hinzu.
"""
)


# -------------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# Öffentliche AI-Funktionen
# -------------------------------------------------------------------

def generate_nutrition_plan(
    prompt: str
) -> dict:
    """
    Erstellt einen strukturierten Ernährungsplan
    inklusive Einkaufsliste.

    Rückgabe:
        {
            "days": [...],
            "shopping_list": [...]
        }
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


def generate_fitness_plan(
    prompt: str,
    expected_training_days: int
) -> dict:
    """
    Erstellt einen strukturierten Fitnessplan.

    Rückgabe:
        {
            "days": [...]
        }
    """

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