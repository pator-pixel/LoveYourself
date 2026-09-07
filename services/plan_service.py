from datetime import date

from models import Plan
from utils.helpers import clean_profile_value


def create_plan_titles(user_id):
    """
    Erstellt eindeutige Titel für Ernährungsplan,
    Fitnessplan und Einkaufsliste.
    """

    today = date.today()

    database_date = today.isoformat()
    display_date = today.strftime("%d-%m-%Y")

    number_of_plans_today = (
        Plan.query
        .filter_by(
            user_id=user_id,
            created_at=database_date
        )
        .count()
    )

    plan_number = number_of_plans_today + 1

    suffix = (
        ""
        if plan_number == 1
        else f"-{plan_number}"
    )

    return (
        f"Ernährungsplan-{display_date}{suffix}",
        f"Fitnessplan-{display_date}{suffix}",
        f"Einkaufsliste-{display_date}{suffix}"
    )


def _format_meal_preferences(meals):
    """
    Formatiert gespeicherte Gerichte für den AI-Prompt.
    """

    if not meals:
        return "Keine"

    cleaned_meals = [
        str(meal).strip()
        for meal in meals
        if str(meal).strip()
    ]

    if not cleaned_meals:
        return "Keine"

    return "\n".join(
        f"- {meal}"
        for meal in cleaned_meals
    )


def build_nutrition_prompt(
    user,
    profile,
    current_weight,
    target_calories,
    liked_meals=None,
    disliked_meals=None
):
    """
    Erstellt den Prompt für den Ernährungsplan.

    liked_meals:
        Gerichte, die der Benutzer mit Daumen hoch
        bewertet hat.

    disliked_meals:
        Gerichte, die der Benutzer mit Daumen runter
        bewertet hat und nicht mehr erscheinen sollen.
    """

    allergies = (
        profile.allergies.strip()
        if profile.allergies
        else "Keine"
    )

    excluded_foods = (
        profile.disliked_foods.strip()
        if profile.disliked_foods
        else "Keine"
    )

    preferred_meals_text = (
        _format_meal_preferences(
            liked_meals
        )
    )

    excluded_meals_text = (
        _format_meal_preferences(
            disliked_meals
        )
    )


    return f"""
Erstelle einen einfachen und übersichtlichen
7-Tage-Ernährungsplan.

Wichtige Angaben:

Name:
{user.username}

Datum:
{date.today().strftime("%d.%m.%Y")}

Aktuelles Gewicht:
{clean_profile_value(current_weight)} kg

Kalorienziel:
{clean_profile_value(target_calories)} kcal pro Tag

Ernährungsform:
{clean_profile_value(profile.diet_type)}

Allergien:
{allergies}

Ausgeschlossene Lebensmittel:
{excluded_foods}

Lebensmittel, die gerne gegessen werden:
{clean_profile_value(profile.liked_foods)}

Lieblingsgerichte aus dem Profil:
{clean_profile_value(profile.favorite_meals)}

Vom Benutzer positiv bewertete Gerichte:
{preferred_meals_text}

Vom Benutzer negativ bewertete und
ausgeschlossene Gerichte:
{excluded_meals_text}

Wünsche für zukünftige Ernährungspläne:
{clean_profile_value(profile.nutrition_wishes)}


Verbindliche Regeln:

- Erstelle genau sieben Tage.
- Verwende nur Tag 1 bis Tag 7.

- Jeder Tag enthält in dieser Reihenfolge:
  Frühstück,
  Mittagessen,
  Snack,
  Abendessen.

- Gib für jede Mahlzeit:
  einen kurzen Namen,
  ungefähre Kalorien,
  Zutaten mit konkreten Mengen
  und eine kurze Zubereitung an.

- Die Tageskalorien sollen ungefähr dem
  angegebenen Kalorienziel entsprechen.


ALLERGIEN UND AUSGESCHLOSSENE LEBENSMITTEL:

- Allergien sind absolute Ausschlusskriterien.
- Verwende keine ausgeschlossenen Lebensmittel.
- Verwende keine verwandten Formen eines Allergens.


GERICHTSBEWERTUNGEN:

- Gerichte unter
  "Vom Benutzer negativ bewertete und
  ausgeschlossene Gerichte"
  dürfen unter keinen Umständen erneut
  im Ernährungsplan vorkommen.

- Verwende negativ bewertete Gerichte auch nicht
  lediglich unter leicht verändertem Namen,
  wenn es sich im Wesentlichen um dasselbe Gericht handelt.

- Wenn zum Beispiel ein bestimmtes Gericht
  ausgeschlossen wurde, ersetze es durch eine
  deutlich andere Mahlzeit.

- Gerichte unter
  "Vom Benutzer positiv bewertete Gerichte"
  dürfen bevorzugt berücksichtigt werden.

- Positiv bewertete Gerichte müssen aber nicht
  zwingend in jedem neuen Plan vorkommen.

- Ein positiv bewertetes Gericht darf gelegentlich
  direkt wiederholt oder sinnvoll variiert werden,
  sofern die Variation weiterhin zu den Vorlieben
  des Benutzers passt.

- Wenn keine Bewertung zu einem Gericht vorhanden ist,
  behandle es neutral.

- Neutral bewertete Gerichte dürfen vorkommen,
  müssen aber nicht erneut verwendet werden.

- Berücksichtige zusätzlich die Lieblingsgerichte
  aus dem Profil, sofern sie mit Allergien,
  ausgeschlossenen Lebensmitteln und Kalorienziel
  vereinbar sind.


ABWECHSLUNG UND EINKAUF:

- Plane bewusst mit wiederkehrenden Zutaten.

- Die Gerichte sollen abwechslungsreich sein,
  dürfen aber dieselben Basiszutaten verwenden.

- Verwende möglichst nur 18 bis 24 Hauptzutaten
  für die gesamte Woche.

- Gewürze, Kräuter und übliche Grundzutaten
  zählen dabei nicht mit.

- Verwende Zutaten möglichst mehrfach
  in unterschiedlichen Gerichten.

- Vermeide Zutaten, die nur für eine einzige
  kleine Mahlzeit gekauft werden müssten,
  wenn eine bereits verwendete Zutat sinnvoll
  eingesetzt werden kann.

- Wenn Fleisch oder Fisch verwendet wird,
  verwende über die gesamte Woche höchstens
  zwei unterschiedliche Fleisch- oder Fischsorten.

- Verwende dieselben Proteinquellen lieber
  in unterschiedlichen Gerichten erneut,
  anstatt ständig neue einzuführen.

- Wiederverwenden bedeutet nicht,
  dass dieselbe Mahlzeit ständig wiederholt
  werden soll.

- Nutze dieselben Zutaten kreativ in
  unterschiedlichen Kombinationen.


EINKAUFSLISTE:

- Erstelle zusätzlich eine kompakte Einkaufsliste.

- Die Einkaufsliste darf ausschließlich Zutaten
  enthalten, die tatsächlich in den Rezepten
  dieses Plans verwendet werden.

- Fasse gleiche Zutaten zusammen.

- Führe dieselbe Zutat nicht mehrfach
  unter leicht unterschiedlichen Namen auf.

- Fasse Mengen gleicher Zutaten nach Möglichkeit
  sinnvoll für die gesamte Woche zusammen.

- Verwende möglichst wenige übersichtliche Kategorien.

- Die Einkaufsliste soll realistisch,
  kompakt und nicht unnötig lang sein.


AUSGABE:

- Keine Einleitung.
- Keine Schlussbemerkung.
- Kein Satz wie:
  "Wenn du möchtest, kann ich den Plan anpassen."
"""



def _format_exercise_preferences(exercises):
    """
    Formatiert gespeicherte Übungen für den AI-Prompt.
    """

    if not exercises:
        return "Keine"

    cleaned_exercises = [
        str(exercise).strip()
        for exercise in exercises
        if str(exercise).strip()
    ]

    if not cleaned_exercises:
        return "Keine"

    return "\n".join(
        f"- {exercise}"
        for exercise in cleaned_exercises
    )


def build_fitness_prompt(
    user,
    profile,
    current_weight,
    liked_exercises=None,
    disliked_exercises=None
):
    """Erstellt den Prompt für den Fitnessplan."""

    gym_text = (
        "Ja"
        if profile.has_gym
        else "Nein"
    )

    training_days = (
        profile.training_days
        or 1
    )

    preferred_exercises_text = (
        _format_exercise_preferences(
            liked_exercises
        )
    )

    excluded_exercises_text = (
        _format_exercise_preferences(
            disliked_exercises
        )
    )

    return f"""
Erstelle einen einfachen und übersichtlichen Fitnessplan.

Wichtige Angaben:

Name:
{user.username}

Datum:
{date.today().strftime("%d.%m.%Y")}

Aktuelles Gewicht:
{clean_profile_value(current_weight)} kg

Anzahl der Trainingstage:
{training_days}

Fitnesslevel:
{clean_profile_value(profile.fitness_level)}

Fitnessstudio:
{gym_text}

Home-Equipment:
{clean_profile_value(profile.home_equipment)}

Körperliche Einschränkungen:
{clean_profile_value(profile.limitations)}

Beliebte Übungen aus dem Profil:
{clean_profile_value(profile.liked_exercises)}

Unbeliebte Übungen aus dem Profil:
{clean_profile_value(profile.disliked_exercises)}

Vom Benutzer positiv bewertete Übungen:
{preferred_exercises_text}

Vom Benutzer negativ bewertete und
ausgeschlossene Übungen:
{excluded_exercises_text}

Bevorzugte Trainingsarten:
{clean_profile_value(profile.preferred_training_types)}

Bevorzugte Trainingsdauer:
{clean_profile_value(profile.preferred_training_duration)}

Wünsche für zukünftige Fitnesspläne:
{clean_profile_value(profile.fitness_wishes)}


Verbindliche Regeln:

- Erstelle genau {training_days} Trainingstage.

- Benenne die Trainingstage nur mit:
  Tag 1, Tag 2 und so weiter.

- Verwende keine festen Wochentage.

- Verwende keine Tageszeiten.

- Verwende nicht:
  Tag A, Tag B, Tag C oder ähnliche Bezeichnungen.

- Halte die Anzahl der Übungen pro Trainingstag
  übersichtlich und passend zur gewünschten Trainingsdauer.

- Jede Übung enthält ausschließlich:
  Name,
  Sätze,
  Wiederholungen oder Dauer,
  Pause
  und eine verständliche Ausführung.

- Verwende keine separate einfache Alternative
  für einzelne Übungen.

- Die einzige Alternative für einen nicht durchgeführten
  Trainingstag ist das Schritte-Ziel am Ende des Tages.


AUSFÜHRUNG DER ÜBUNGEN:

- Erkläre jede Übung so verständlich,
  dass auch eine Person ohne Trainingserfahrung
  weiß, was sie tun soll.

- Schreibe nicht nur allgemeine Aussagen wie:
  "Bein anheben",
  "Rücken gerade halten"
  oder
  "kontrolliert ausführen".

- Beschreibe zuerst die Ausgangsposition.

- Erkläre konkret,
  wo Hände, Füße, Beine oder Oberkörper
  positioniert werden sollen,
  soweit dies für die Übung wichtig ist.

- Beschreibe anschließend Schritt für Schritt,
  welches Körperteil sich in welche Richtung bewegt.

- Erkläre,
  wie weit die Bewegung ungefähr ausgeführt werden soll,
  wenn dies für die Übung sinnvoll ist.

- Nenne wichtige Hinweise zur Körperhaltung,
  zum Beispiel:
  Rückenposition,
  Knieposition,
  Fußstellung
  oder kontrollierte Bewegung.

- Beschreibe zum Schluss,
  wie die Person wieder kontrolliert
  in die Ausgangsposition zurückkehrt.

- Wenn Seiten gewechselt werden müssen,
  sage ausdrücklich,
  wann die andere Seite trainiert wird.

- Wenn eine Übung auf Zeit ausgeführt wird,
  erkläre auch,
  welche Position während dieser Zeit gehalten wird.

- Verwende einfache Alltagssprache.

- Verwende Fachbegriffe nur,
  wenn sie für die Übung notwendig sind,
  und erkläre sie verständlich.

- Die Erklärung soll konkret und hilfreich sein,
  aber nicht unnötig lang werden.


ÜBUNGSBEWERTUNGEN:

- Übungen unter
  "Vom Benutzer negativ bewertete und
  ausgeschlossene Übungen"
  dürfen unter keinen Umständen erneut
  im Fitnessplan vorkommen.

- Verwende negativ bewertete Übungen auch nicht
  lediglich unter leicht verändertem Namen,
  wenn es sich im Wesentlichen um dieselbe Übung handelt.

- Wähle stattdessen eine deutlich andere Übung,
  die sinnvoll zum Trainingsziel und Fitnesslevel passt.

- Übungen unter
  "Vom Benutzer positiv bewertete Übungen"
  dürfen bevorzugt berücksichtigt werden.

- Positiv bewertete Übungen müssen nicht
  in jedem neuen Fitnessplan vorkommen.

- Wenn keine Bewertung zu einer Übung vorhanden ist,
  behandle sie neutral.

- Neutral bewertete Übungen dürfen erneut vorkommen,
  müssen aber nicht erneut verwendet werden.


VORLIEBEN UND EINSCHRÄNKUNGEN:

- Verwende keine unbeliebten Übungen aus dem Profil.

- Bevorzuge beliebte Übungen aus dem Profil
  und positiv bewertete Übungen.

- Negativ bewertete Übungen und unbeliebte Übungen
  aus dem Profil haben Vorrang vor positiven Vorlieben.

- Bevorzuge die angegebenen Trainingsarten.

- Berücksichtige körperliche Einschränkungen
  bei jeder einzelnen Übung.

- Wähle keine Übung,
  die offensichtlich mit einer angegebenen
  körperlichen Einschränkung kollidiert.

- Berücksichtige die gewünschte Trainingsdauer.

- Passe Übungen und Umfang
  an das angegebene Fitnesslevel an.


FITNESSSTUDIO UND EQUIPMENT:

- Wenn kein Fitnessstudio vorhanden ist,
  verwende ausschließlich:
  Körpergewicht
  und das angegebene verfügbare Equipment.

- Erfinde kein Equipment,
  das nicht angegeben wurde.

- Wenn Fitnessstudio vorhanden ist,
  dürfen passende Geräte und Gewichte
  verwendet werden.


SCHRITTE-ALTERNATIVE:

- Ergänze pro Trainingstag genau
  ein kurzes Schritte-Ziel.

- Dieses Schritte-Ziel dient als Alternative,
  falls die Trainingseinheit an diesem Tag
  nicht durchgeführt wird.

- Halte diese Angabe kurz,
  zum Beispiel:
  "2.000 zusätzliche Schritte".

- Verwende keine zusätzliche Alternative
  innerhalb einzelner Übungen.


AUSGABE:

- Keine Einleitung.

- Keine Schlussbemerkung.

- Kein eigenes Kapitel für Trainingsziel.

- Kein eigenes Kapitel für Trainingsmöglichkeiten.

- Kein eigenes Kapitel für Regeneration.

- Keine Motivationsfloskeln.

- Keine medizinischen Versprechen.
"""