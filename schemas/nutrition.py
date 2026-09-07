from typing import List

from pydantic import BaseModel, Field


class Meal(BaseModel):
    name: str = Field(
        description=(
            "Kurzer Name der Mahlzeit."
        )
    )

    calories: int = Field(
        ge=0,
        description=(
            "Ungefähre Kalorienzahl der Mahlzeit."
        )
    )

    ingredients: List[str] = Field(
        min_length=1,
        description=(
            "Zutaten mit konkreten Mengenangaben, "
            "zum Beispiel '150 g Kichererbsen'."
        )
    )

    preparation: List[str] = Field(
        min_length=1,
        max_length=6,
        description=(
            "Kurze Zubereitungsschritte in sinnvoller Reihenfolge."
        )
    )


class NutritionDay(BaseModel):
    day: int = Field(
        ge=1,
        le=7,
        description=(
            "Tag als Zahl zwischen 1 und 7."
        )
    )

    breakfast: Meal
    lunch: Meal
    snack: Meal
    dinner: Meal


class ShoppingCategory(BaseModel):
    category: str = Field(
        description=(
            "Kurzer Kategoriename, zum Beispiel Gemüse, "
            "Obst oder Proteinquellen."
        )
    )

    items: List[str] = Field(
        description=(
            "Zusammengefasste Zutaten mit benötigten Mengen. "
            "Keine Erklärungen und keine doppelten Zutaten."
        )
    )


class NutritionPlanResult(BaseModel):
    days: List[NutritionDay] = Field(
        min_length=7,
        max_length=7,
        description=(
            "Genau sieben Ernährungstage."
        )
    )

    shopping_list: List[ShoppingCategory] = Field(
        description=(
            "Kompakte Einkaufsliste, nach sinnvollen "
            "Kategorien sortiert."
        )
    )