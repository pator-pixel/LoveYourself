from typing import List

from pydantic import BaseModel, Field


class Exercise(BaseModel):
    name: str = Field(
        description=(
            "Kurzer, eindeutiger Name der Übung."
        )
    )

    sets: str = Field(
        description=(
            "Anzahl der Sätze, zum Beispiel 3."
        )
    )

    repetitions: str = Field(
        description=(
            "Wiederholungen oder Zeit, zum Beispiel "
            "10 bis 12 Wiederholungen oder 30 Sekunden."
        )
    )

    pause: str = Field(
        description=(
            "Kurze Pausenangabe zwischen den Sätzen, "
            "zum Beispiel 60 Sekunden."
        )
    )

    instructions: str = Field(
        description=(
            "Eine leicht verständliche und konkrete Erklärung "
            "zur Ausführung der Übung. "
            "Beschreibe zuerst die Ausgangsposition, dann die Bewegung, "
            "anschließend wichtige Hinweise zur Körperhaltung und zuletzt, "
            "wie die Bewegung kontrolliert beendet wird. "
            "Die Erklärung soll so verständlich sein, dass auch eine Person "
            "ohne Trainingserfahrung die Übung sicher nachvollziehen kann. "
            "Keine Fachbegriffe ohne Erklärung und keine unnötig langen Texte."
        )
    )


class FitnessDay(BaseModel):
    day: int = Field(
        ge=1,
        description=(
            "Trainingstag als Zahl: Tag 1, Tag 2 und so weiter."
        )
    )

    exercises: List[Exercise] = Field(
        min_length=3,
        description=(
            "Eine kurze und übersichtliche Übungsliste. "
            "Jede Übung enthält Name, Sätze, Wiederholungen oder Dauer, "
            "Pause und eine verständliche Ausführung."
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
            "Genau so viele Trainingstage, "
            "wie im Profil angegeben."
        )
    )