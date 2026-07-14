import json
import os
import random
import string
from datetime import date

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from ai_service import (
    generate_fitness_plan,
    generate_nutrition_plan
)
from models import (
    db,
    Plan,
    PlanFeedback,
    Profile,
    SupportMessage,
    User,
    WeightEntry
)


# ============================================================
# APP-KONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///love_yourself.db"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

db.init_app(app)


# Der Benutzername des Administrators wird aus der .env geladen.
#
# Beispiel:
# ADMIN_USERNAME=Patricia
#
# Ohne Eintrag gilt standardmäßig der Benutzername "admin".
ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
).strip()


SUPPORT_CATEGORIES = [
    "Technisches Problem",
    "Problem mit einem Plan",
    "Konto und Profil",
    "Verbesserungsvorschlag",
    "Sicherheit oder unangemessener Inhalt",
    "Sonstiges"
]


SUPPORT_STATUS_VALUES = [
    "Offen",
    "In Bearbeitung",
    "Beantwortet",
    "Geschlossen"
]


LOVE_MESSAGES_DE = [
    (
        "Es ist nicht schlimm, wenn du heute einen schlechten "
        "Tag hattest. Morgen ist eine neue Chance."
    ),
    (
        "Perfektion ist nicht das Ziel. Beständigkeit ist "
        "wichtiger als ein einzelner perfekter Tag."
    ),
    (
        "Ein Spaziergang von 20 Minuten ist besser als gar "
        "keine Bewegung. Jeder Schritt zählt."
    ),
    (
        "Schlaf ist kein Luxus. Er ist ein wichtiger Teil "
        "deiner Gesundheit."
    ),
    (
        "Du arbeitest an deiner Gesundheit, nicht an deinem "
        "Wert als Mensch. Du bist jetzt schon wertvoll."
    )
]


# ============================================================
# ALLGEMEINE HILFSFUNKTIONEN
# ============================================================

def is_valid_password(password):
    """
    Prüft die Passwortregeln.

    Mindestens:
    - 8 Zeichen
    - ein Großbuchstabe
    - ein Kleinbuchstabe
    - eine Zahl
    - ein Sonderzeichen
    """

    if not password or len(password) < 8:
        return False

    return (
        any(
            character.isupper()
            for character in password
        )
        and any(
            character.islower()
            for character in password
        )
        and any(
            character.isdigit()
            for character in password
        )
        and any(
            character in string.punctuation
            for character in password
        )
    )


def generate_temporary_password():
    """
    Erstellt ein zufälliges temporäres Passwort.
    """

    random_part = "".join(
        random.choices(
            string.ascii_letters
            + string.digits,
            k=8
        )
    )

    return f"Love{random_part}!"


def clean_profile_value(value):
    """
    Verhindert leere Werte in AI-Prompts.
    """

    if value is None or value == "":
        return "Keine Angabe"

    return value


def parse_json_data(json_text, fallback):
    """
    Wandelt gespeicherte JSON-Texte wieder in
    Python-Listen oder Dictionaries um.
    """

    if not json_text:
        return fallback

    try:
        return json.loads(json_text)

    except (
        json.JSONDecodeError,
        TypeError
    ):
        return fallback


def form_list(field_name):
    """
    Liest mehrere dynamische Formularfelder ein
    und speichert sie zeilenweise.
    """

    return "\n".join(
        item.strip()
        for item in request.form.getlist(field_name)
        if item.strip()
    )


def join_selected_values(values):
    """
    Wandelt ausgewählte Checkbox-Werte in
    einen zeilenweisen Text um.
    """

    return "\n".join(
        value.strip()
        for value in values
        if value.strip()
    )


def merge_lines(existing_value, new_value):
    """
    Fügt neue Angaben zu einem bestehenden
    zeilenweisen Text hinzu.

    Doppelte Einträge werden vermieden.
    """

    existing_items = []

    if existing_value:
        existing_items = [
            item.strip()
            for item in existing_value.splitlines()
            if item.strip()
        ]

    new_items = []

    if new_value:
        new_items = [
            item.strip()
            for item in new_value.splitlines()
            if item.strip()
        ]

    combined_items = existing_items.copy()

    known_items = {
        item.casefold()
        for item in combined_items
    }

    for item in new_items:
        normalized_item = item.casefold()

        if normalized_item not in known_items:
            combined_items.append(item)
            known_items.add(normalized_item)

    return "\n".join(combined_items)


def combine_choice_fields(
    checkbox_field,
    custom_field
):
    """
    Verbindet vorgegebene Auswahlchips mit
    einem freien Sonstiges-Feld.
    """

    selected_values = [
        value.strip()
        for value in request.form.getlist(
            checkbox_field
        )
        if value.strip()
    ]

    custom_value = request.form.get(
        custom_field,
        ""
    ).strip()

    if custom_value:
        custom_items = [
            item.strip()
            for item in custom_value.splitlines()
            if item.strip()
        ]

        known_items = {
            value.casefold()
            for value in selected_values
        }

        for item in custom_items:
            normalized_item = item.casefold()

            if normalized_item not in known_items:
                selected_values.append(item)
                known_items.add(normalized_item)

    return "\n".join(selected_values)


def get_logged_in_user():
    """
    Gibt den aktuell angemeldeten Benutzer zurück.
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(
        User,
        user_id
    )


def user_is_admin(user):
    """
    Prüft, ob der Benutzer der konfigurierte
    Administrator ist.
    """

    if not user:
        return False

    return (
        user.username.casefold()
        == ADMIN_USERNAME.casefold()
    )


def get_owned_plan(plan_id, user_id):
    """
    Lädt einen Plan nur, wenn er dem angemeldeten
    Benutzer gehört.
    """

    return Plan.query.filter_by(
        id=plan_id,
        user_id=user_id
    ).first()


@app.context_processor
def inject_navigation_state():
    """
    Diese Werte stehen automatisch in allen Templates
    zur Verfügung.

    Dadurch kann base.html die Navigation abhängig
    vom Login- und Adminstatus anzeigen.
    """

    current_user = get_logged_in_user()

    return {
        "current_user": current_user,
        "is_logged_in": current_user is not None,
        "is_admin": user_is_admin(current_user)
    }


# ============================================================
# GEWICHT UND KALORIEN
# ============================================================

def get_current_weight(user_id, profile):
    """
    Gibt den neuesten Gewichtseintrag zurück.

    Wenn noch kein Tracking vorhanden ist,
    wird das Startgewicht aus dem Profil verwendet.
    """

    latest_entry = (
        WeightEntry.query
        .filter_by(user_id=user_id)
        .order_by(
            WeightEntry.date.desc(),
            WeightEntry.id.desc()
        )
        .first()
    )

    if latest_entry:
        return latest_entry.weight

    return (
        profile.weight
        if profile
        else None
    )


def calculate_calories(
    profile,
    current_weight=None
):
    """
    Berechnet:

    - Grundumsatz
    - Erhaltungsbedarf
    - tägliches Kalorienziel
    """

    if not profile:
        return None, None, None

    if (
        not profile.age
        or not profile.height
        or not profile.gender
    ):
        return None, None, None

    weight_for_calculation = (
        current_weight
        if current_weight is not None
        else profile.weight
    )

    if weight_for_calculation is None:
        return None, None, None

    if profile.gender == "male":
        bmr = (
            10 * weight_for_calculation
            + 6.25 * profile.height
            - 5 * profile.age
            + 5
        )

    else:
        bmr = (
            10 * weight_for_calculation
            + 6.25 * profile.height
            - 5 * profile.age
            - 161
        )

    activity_factors = {
        "low": 1.2,
        "medium": 1.55,
        "high": 1.75
    }

    activity_factor = activity_factors.get(
        profile.activity_level,
        1.2
    )

    maintenance_calories = round(
        bmr * activity_factor
    )

    if profile.goal_weight is None:
        target_calories = maintenance_calories

    elif profile.goal_weight < weight_for_calculation:
        target_calories = (
            maintenance_calories - 500
        )

    elif profile.goal_weight > weight_for_calculation:
        target_calories = (
            maintenance_calories + 300
        )

    else:
        target_calories = maintenance_calories

    target_calories = max(
        target_calories,
        1200
    )

    return (
        round(bmr),
        maintenance_calories,
        target_calories
    )


# ============================================================
# PLANNAMEN
# ============================================================

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

    plan_number = (
        number_of_plans_today + 1
    )

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


# ============================================================
# AI-PROMPTS
# ============================================================

def build_nutrition_prompt(
    user,
    profile,
    current_weight,
    target_calories
):
    """
    Erstellt den Prompt für den Ernährungsplan.
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

Lieblingsgerichte:
{clean_profile_value(profile.favorite_meals)}

Wünsche für zukünftige Ernährungspläne:
{clean_profile_value(profile.nutrition_wishes)}

Verbindliche Regeln:

- Erstelle genau sieben Tage.
- Verwende nur Tag 1 bis Tag 7.
- Jeder Tag enthält Frühstück, Mittagessen,
  Abendessen und einen Snack.
- Halte alle Mahlzeitennamen kurz.
- Gib pro Mahlzeit ungefähre Kalorien an.
- Die Tageskalorien sollen ungefähr dem
  angegebenen Kalorienziel entsprechen.
- Allergien sind absolute Ausschlusskriterien.
- Verwende keine ausgeschlossenen Lebensmittel.
- Verwende keine verwandten Formen eines Allergens.
- Berücksichtige Lieblingsgerichte und Vorlieben,
  sofern sie zum Kalorienziel passen.
- Erstelle zusätzlich eine kurze Einkaufsliste.
- Führe gleiche Zutaten nur einmal auf.
- Die Einkaufsliste darf nur Zutaten enthalten,
  die im Ernährungsplan vorkommen.
- Keine Einleitung.
- Keine Schlussbemerkung.
- Keine Kochanleitung.
- Kein Satz wie:
  "Wenn du möchtest, kann ich den Plan anpassen."
"""


def build_fitness_prompt(
    user,
    profile,
    current_weight
):
    """
    Erstellt den Prompt für den Fitnessplan.
    """

    gym_text = (
        "Ja"
        if profile.has_gym
        else "Nein"
    )

    training_days = (
        profile.training_days
        or 1
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

Beliebte Übungen:
{clean_profile_value(profile.liked_exercises)}

Unbeliebte Übungen:
{clean_profile_value(profile.disliked_exercises)}

Bevorzugte Trainingsarten:
{clean_profile_value(profile.preferred_training_types)}

Bevorzugte Trainingsdauer:
{clean_profile_value(profile.preferred_training_duration)}

Wünsche für zukünftige Fitnesspläne:
{clean_profile_value(profile.fitness_wishes)}

Verbindliche Regeln:

- Erstelle genau {training_days} Trainingstage.
- Benenne sie nur Tag 1, Tag 2 und so weiter.
- Verwende keine festen Wochentage.
- Verwende keine Tageszeiten.
- Verwende nicht Tag A, Tag B oder Tag C.
- Halte die Anzahl der Übungen übersichtlich.
- Jede Übung enthält nur:
  Name, Sätze, Wiederholungen oder Dauer,
  Pause und eine kurze Alternative.
- Verwende keine unbeliebten Übungen.
- Bevorzuge beliebte Übungen und Trainingsarten.
- Berücksichtige körperliche Einschränkungen.
- Berücksichtige die gewünschte Trainingsdauer.
- Wenn kein Fitnessstudio vorhanden ist,
  verwende nur Körpergewicht und das angegebene Equipment.
- Ergänze pro Trainingstag nur ein kurzes Schritte-Ziel
  als Alternative.
- Keine Einleitung.
- Keine Schlussbemerkung.
- Kein eigenes Kapitel für Trainingsziel.
- Kein eigenes Kapitel für Trainingsmöglichkeiten.
- Kein eigenes Kapitel für Regeneration.
- Keine langen Übungserklärungen.
"""


# ============================================================
# ÖFFENTLICHE SEITEN
# ============================================================

@app.route("/")
def index():
    return render_template(
        "home.html",
        message=random.choice(LOVE_MESSAGES_DE)
    )


@app.route("/about")
def about():
    """
    Die Seite:
    Die Idee hinter Love Yourself
    """

    return render_template(
        "about.html"
    )


@app.route("/impressum")
def impressum():
    return render_template(
        "impressum.html"
    )


# ============================================================
# REGISTRIERUNG UND LOGIN
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():
    error = None

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        language = request.form.get(
            "language",
            "de"
        )

        if len(username) < 3:
            error = (
                "Der Benutzername muss mindestens "
                "3 Zeichen lang sein."
            )

        elif User.query.filter_by(
            username=username
        ).first():
            error = (
                "Dieser Benutzername ist bereits vergeben."
            )

        elif password != confirm_password:
            error = (
                "Die Passwörter stimmen nicht überein."
            )

        elif not is_valid_password(password):
            error = (
                "Das Passwort muss mindestens 8 Zeichen, "
                "einen Großbuchstaben, einen Kleinbuchstaben, "
                "eine Zahl und ein Sonderzeichen enthalten."
            )

        else:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(
                    password
                ),
                language=language
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(
                url_for("login")
            )

    return render_template(
        "register.html",
        error=error
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    error = None

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):
            session.clear()
            session["user_id"] = user.id

            return redirect(
                url_for("dashboard")
            )

        error = (
            "Benutzername oder Passwort ist falsch."
        )

    return render_template(
        "login.html",
        error=error
    )


@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():
    temporary_password = None
    error = None

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            error = (
                "Dieser Benutzername wurde nicht gefunden."
            )

        else:
            temporary_password = (
                generate_temporary_password()
            )

            user.password_hash = (
                generate_password_hash(
                    temporary_password
                )
            )

            db.session.commit()

    return render_template(
        "forgot_password.html",
        error=error,
        temporary_password=temporary_password
    )


@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    error = None
    success = None

    if request.method == "POST":
        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not check_password_hash(
            user.password_hash,
            current_password
        ):
            error = (
                "Das aktuelle Passwort ist falsch."
            )

        elif new_password != confirm_password:
            error = (
                "Die neuen Passwörter stimmen "
                "nicht überein."
            )

        elif not is_valid_password(
            new_password
        ):
            error = (
                "Das neue Passwort erfüllt die "
                "Sicherheitsregeln nicht."
            )

        else:
            user.password_hash = (
                generate_password_hash(
                    new_password
                )
            )

            db.session.commit()

            success = (
                "Dein Passwort wurde erfolgreich geändert."
            )

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    entries = (
        WeightEntry.query
        .filter_by(user_id=user.id)
        .order_by(
            WeightEntry.date.asc(),
            WeightEntry.id.asc()
        )
        .all()
    )

    start_weight = (
        profile_data.weight
        if profile_data
        else None
    )

    goal_weight = (
        profile_data.goal_weight
        if profile_data
        else None
    )

    current_weight = get_current_weight(
        user.id,
        profile_data
    )

    remaining_weight = None
    weight_change_text = None
    progress_percent = None

    if (
        current_weight is not None
        and goal_weight is not None
        and start_weight is not None
    ):
        if goal_weight < start_weight:
            remaining_weight = max(
                round(
                    current_weight - goal_weight,
                    1
                ),
                0
            )

        elif goal_weight > start_weight:
            remaining_weight = max(
                round(
                    goal_weight - current_weight,
                    1
                ),
                0
            )

        else:
            remaining_weight = 0

    if (
        start_weight is not None
        and current_weight is not None
    ):
        difference = round(
            current_weight - start_weight,
            1
        )

        if difference < 0:
            weight_change_text = (
                f"{abs(difference)} kg abgenommen"
            )

        elif difference > 0:
            weight_change_text = (
                f"{difference} kg zugenommen"
            )

        else:
            weight_change_text = (
                "Keine Veränderung"
            )

    if (
        start_weight is not None
        and current_weight is not None
        and goal_weight is not None
    ):
        if goal_weight < start_weight:
            total_goal = (
                start_weight - goal_weight
            )

            current_progress = (
                start_weight - current_weight
            )

        elif goal_weight > start_weight:
            total_goal = (
                goal_weight - start_weight
            )

            current_progress = (
                current_weight - start_weight
            )

        else:
            total_goal = 0
            current_progress = 0

        if total_goal > 0:
            progress_percent = round(
                current_progress
                / total_goal
                * 100
            )

            progress_percent = max(
                0,
                min(
                    progress_percent,
                    100
                )
            )

    (
        bmr,
        maintenance_calories,
        target_calories
    ) = calculate_calories(
        profile_data,
        current_weight
    )

    return render_template(
        "dashboard.html",
        user=user,
        message=random.choice(
            LOVE_MESSAGES_DE
        ),
        current_weight=current_weight,
        goal_weight=goal_weight,
        remaining_weight=remaining_weight,
        start_weight=start_weight,
        weight_change_text=weight_change_text,
        progress_percent=progress_percent,
        total_entries=len(entries),
        bmr=bmr,
        maintenance_calories=maintenance_calories,
        target_calories=target_calories
    )


# ============================================================
# PROFIL
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    error = None

    if request.method == "POST":
        try:
            age = (
                int(request.form.get("age"))
                if request.form.get("age")
                else None
            )

            height = (
                float(request.form.get("height"))
                if request.form.get("height")
                else None
            )

            start_weight = (
                float(request.form.get("weight"))
                if request.form.get("weight")
                else None
            )

            goal_weight = (
                float(request.form.get("goal_weight"))
                if request.form.get("goal_weight")
                else None
            )

            training_days = (
                int(
                    request.form.get(
                        "training_days"
                    )
                )
                if request.form.get(
                    "training_days"
                )
                else None
            )

        except ValueError:
            error = (
                "Bitte überprüfe deine Zahlenangaben."
            )

            age = None
            height = None
            start_weight = None
            goal_weight = None
            training_days = None

        if (
            age is not None
            and not 16 <= age <= 120
        ):
            error = (
                "Das Alter muss zwischen "
                "16 und 120 liegen."
            )

        if (
            height is not None
            and not 100 <= height <= 250
        ):
            error = (
                "Die Größe muss zwischen "
                "100 und 250 cm liegen."
            )

        if (
            start_weight is not None
            and not 30 <= start_weight <= 300
        ):
            error = (
                "Das Startgewicht muss zwischen "
                "30 und 300 kg liegen."
            )

        if (
            goal_weight is not None
            and not 30 <= goal_weight <= 300
        ):
            error = (
                "Das Zielgewicht muss zwischen "
                "30 und 300 kg liegen."
            )

        if (
            training_days is not None
            and not 1 <= training_days <= 7
        ):
            error = (
                "Trainingstage müssen zwischen "
                "1 und 7 liegen."
            )

        if error:
            return render_template(
                "profile.html",
                user=user,
                profile=profile_data,
                error=error
            )

        if profile_data is None:
            profile_data = Profile(
                user_id=user.id
            )

            db.session.add(
                profile_data
            )

        profile_data.age = age

        profile_data.gender = (
            request.form.get("gender")
        )

        profile_data.height = height
        profile_data.weight = start_weight
        profile_data.goal_weight = goal_weight

        profile_data.activity_level = (
            request.form.get(
                "activity_level"
            )
        )

        profile_data.diet_type = (
            request.form.get(
                "diet_type"
            )
        )

        profile_data.allergies = form_list(
            "allergies_item"
        )

        profile_data.diseases = form_list(
            "diseases_item"
        )

        profile_data.limitations = form_list(
            "limitations_item"
        )

        profile_data.liked_foods = form_list(
            "liked_foods_item"
        )

        profile_data.disliked_foods = form_list(
            "disliked_foods_item"
        )

        profile_data.favorite_meals = form_list(
            "favorite_meals_item"
        )

        profile_data.nutrition_wishes = (
            combine_choice_fields(
                "nutrition_wishes_choices",
                "nutrition_wishes_other"
            )
        )

        profile_data.fitness_level = (
            request.form.get(
                "fitness_level"
            )
        )

        profile_data.training_days = (
            training_days
        )

        profile_data.has_gym = (
            request.form.get("has_gym")
            == "yes"
        )

        profile_data.home_equipment = form_list(
            "home_equipment_item"
        )

        profile_data.liked_exercises = form_list(
            "liked_exercises_item"
        )

        profile_data.disliked_exercises = form_list(
            "disliked_exercises_item"
        )

        profile_data.preferred_training_types = (
            combine_choice_fields(
                "preferred_training_types_choices",
                "preferred_training_types_other"
            )
        )

        profile_data.preferred_training_duration = (
            request.form.get(
                "preferred_training_duration",
                ""
            ).strip()
            or None
        )

        profile_data.fitness_wishes = (
            combine_choice_fields(
                "fitness_wishes_choices",
                "fitness_wishes_other"
            )
        )

        # Nicht mehr genutzte Felder leeren.
        profile_data.preferred_training_time = None
        profile_data.nutrition_notes = None
        profile_data.fitness_notes = None

        db.session.commit()

        return redirect(
            url_for(
                "profile",
                saved="1"
            )
        )

    return render_template(
        "profile.html",
        user=user,
        profile=profile_data,
        error=error
    )


@app.route("/profile-view")
def profile_view():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    return render_template(
        "profile_view.html",
        user=user,
        profile=profile_data
    )


# ============================================================
# GEWICHTSTRACKING
# ============================================================

@app.route(
    "/weight",
    methods=["GET", "POST"]
)
def weight_tracking():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    error = None

    if request.method == "POST":
        weight_text = request.form.get(
            "weight",
            ""
        ).strip()

        entry_date = request.form.get(
            "date",
            ""
        ).strip()

        try:
            weight_value = float(
                weight_text
            )

        except ValueError:
            weight_value = None

            error = (
                "Bitte gib ein gültiges Gewicht ein."
            )

        if weight_value is not None:
            if not 30 <= weight_value <= 300:
                error = (
                    "Bitte gib ein realistisches Gewicht "
                    "zwischen 30 und 300 kg ein."
                )

            else:
                new_entry = WeightEntry(
                    weight=weight_value,
                    date=(
                        entry_date
                        if entry_date
                        else date.today().isoformat()
                    ),
                    user_id=user.id
                )

                db.session.add(
                    new_entry
                )

                db.session.commit()

                return redirect(
                    url_for(
                        "weight_tracking"
                    )
                )

    entries = (
        WeightEntry.query
        .filter_by(user_id=user.id)
        .order_by(
            WeightEntry.date.desc(),
            WeightEntry.id.desc()
        )
        .all()
    )

    return render_template(
        "weight.html",
        entries=entries,
        today=date.today().isoformat(),
        error=error
    )


@app.route(
    "/weight/<int:entry_id>/delete",
    methods=["POST"]
)
def delete_weight_entry(entry_id):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    entry = WeightEntry.query.filter_by(
        id=entry_id,
        user_id=user.id
    ).first()

    if entry:
        db.session.delete(
            entry
        )

        db.session.commit()

    return redirect(
        url_for("weight_tracking")
    )


# ============================================================
# PLÄNE
# ============================================================

@app.route("/generate-plan")
def generate_plan():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile_data:
        return redirect(
            url_for("profile")
        )

    current_weight = get_current_weight(
        user.id,
        profile_data
    )

    (
        _,
        _,
        target_calories
    ) = calculate_calories(
        profile_data,
        current_weight
    )

    if target_calories is None:
        return (
            "Der Plan konnte nicht erstellt werden. "
            "Bitte fülle Alter, Geschlecht, Größe, "
            "Gewicht und Aktivitätslevel aus.",
            400
        )

    training_days = (
        profile_data.training_days
        or 1
    )

    nutrition_prompt = build_nutrition_prompt(
        user,
        profile_data,
        current_weight,
        target_calories
    )

    fitness_prompt = build_fitness_prompt(
        user,
        profile_data,
        current_weight
    )

    try:
        nutrition_result = (
            generate_nutrition_plan(
                nutrition_prompt
            )
        )

        fitness_result = (
            generate_fitness_plan(
                fitness_prompt,
                expected_training_days=training_days
            )
        )

    except Exception as error:
        app.logger.exception(
            "Fehler bei der AI-Planerstellung"
        )

        return (
            "Der AI-Plan konnte nicht erstellt werden. "
            f"Fehler: {error}",
            503
        )

    nutrition_days = (
        nutrition_result.get(
            "days",
            []
        )
    )

    shopping_list = (
        nutrition_result.get(
            "shopping_list",
            []
        )
    )

    fitness_days = (
        fitness_result.get(
            "days",
            []
        )
    )

    if len(nutrition_days) != 7:
        return (
            "Der Ernährungsplan enthält nicht "
            "genau sieben Tage.",
            503
        )

    if len(fitness_days) != training_days:
        return (
            "Der Fitnessplan enthält nicht die "
            "gewünschte Anzahl an Trainingstagen.",
            503
        )

    if not shopping_list:
        return (
            "Die Einkaufsliste wurde nicht erstellt.",
            503
        )

    (
        nutrition_title,
        fitness_title,
        shopping_title
    ) = create_plan_titles(
        user.id
    )

    new_plan = Plan(
        nutrition_title=nutrition_title,
        fitness_title=fitness_title,
        shopping_title=shopping_title,
        created_at=date.today().isoformat(),
        current_weight=current_weight,
        calories=target_calories,
        allergies_snapshot=(
            profile_data.allergies
            or ""
        ),
        excluded_foods_snapshot=(
            profile_data.disliked_foods
            or ""
        ),
        nutrition_prompt=nutrition_prompt,
        fitness_prompt=fitness_prompt,
        nutrition_data=json.dumps(
            nutrition_days,
            ensure_ascii=False
        ),
        fitness_data=json.dumps(
            fitness_days,
            ensure_ascii=False
        ),
        shopping_data=json.dumps(
            shopping_list,
            ensure_ascii=False
        ),
        user_id=user.id
    )

    db.session.add(
        new_plan
    )

    db.session.commit()

    return redirect(
        url_for("plans")
    )


@app.route("/plans")
def plans():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    user_plans = (
        Plan.query
        .filter_by(user_id=user.id)
        .order_by(
            Plan.id.desc()
        )
        .all()
    )

    return render_template(
        "plans.html",
        plans=user_plans
    )


@app.route("/plans/<int:plan_id>")
def view_plan(plan_id):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    nutrition_days = parse_json_data(
        plan.nutrition_data,
        []
    )

    fitness_days = parse_json_data(
        plan.fitness_data,
        []
    )

    shopping_categories = parse_json_data(
        plan.shopping_data,
        []
    )

    return render_template(
        "plan.html",
        plan=plan,
        user=user,
        nutrition_days=nutrition_days,
        fitness_days=fitness_days,
        shopping_categories=shopping_categories
    )


# ============================================================
# PLAN-FEEDBACK
# ============================================================

@app.route(
    "/plans/<int:plan_id>/feedback/<feedback_type>",
    methods=["GET", "POST"]
)
def plan_feedback(
    plan_id,
    feedback_type
):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    if feedback_type not in {
        "nutrition",
        "fitness"
    }:
        abort(400)

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile_data:
        return redirect(
            url_for("profile")
        )

    error = None

    if request.method == "POST":
        rating_text = request.form.get(
            "rating",
            ""
        ).strip()

        rating = None

        if rating_text:
            try:
                rating = int(
                    rating_text
                )

            except ValueError:
                error = (
                    "Bitte wähle eine gültige "
                    "Bewertung aus."
                )

        if (
            rating is not None
            and not 1 <= rating <= 5
        ):
            error = (
                "Die Bewertung muss zwischen "
                "1 und 5 liegen."
            )

        if error:
            return render_template(
                "plan_feedback.html",
                plan=plan,
                feedback_type=feedback_type,
                error=error
            )

        liked_items = request.form.get(
            "liked_items",
            ""
        ).strip()

        disliked_items = request.form.get(
            "disliked_items",
            ""
        ).strip()

        favorite_meals = request.form.get(
            "favorite_meals",
            ""
        ).strip()

        wishes = request.form.get(
            "wishes",
            ""
        ).strip()

        comment = request.form.get(
            "comment",
            ""
        ).strip()

        selected_preferences = (
            join_selected_values(
                request.form.getlist(
                    "selected_preferences"
                )
            )
        )

        preferred_training_duration = (
            request.form.get(
                "preferred_training_duration",
                ""
            ).strip()
        )

        feedback = PlanFeedback(
            feedback_type=feedback_type,
            rating=rating,
            liked_items=liked_items,
            disliked_items=disliked_items,
            favorite_meals=favorite_meals,
            selected_preferences=selected_preferences,
            preferred_training_duration=(
                preferred_training_duration
                or None
            ),
            preferred_training_time=None,
            wishes=wishes,
            comment=comment,
            created_at=date.today().isoformat(),
            plan_id=plan.id,
            user_id=user.id
        )

        db.session.add(
            feedback
        )

        if feedback_type == "nutrition":
            profile_data.liked_foods = merge_lines(
                profile_data.liked_foods,
                liked_items
            )

            profile_data.disliked_foods = merge_lines(
                profile_data.disliked_foods,
                disliked_items
            )

            profile_data.favorite_meals = merge_lines(
                profile_data.favorite_meals,
                favorite_meals
            )

            profile_data.nutrition_wishes = merge_lines(
                profile_data.nutrition_wishes,
                selected_preferences
            )

            profile_data.nutrition_wishes = merge_lines(
                profile_data.nutrition_wishes,
                wishes
            )

        else:
            profile_data.liked_exercises = merge_lines(
                profile_data.liked_exercises,
                liked_items
            )

            profile_data.disliked_exercises = merge_lines(
                profile_data.disliked_exercises,
                disliked_items
            )

            profile_data.preferred_training_types = (
                merge_lines(
                    profile_data.preferred_training_types,
                    selected_preferences
                )
            )

            if preferred_training_duration:
                profile_data.preferred_training_duration = (
                    preferred_training_duration
                )

            profile_data.fitness_wishes = merge_lines(
                profile_data.fitness_wishes,
                wishes
            )

        db.session.commit()

        return redirect(
            url_for(
                "view_plan",
                plan_id=plan.id,
                feedback_saved="1"
            )
        )

    return render_template(
        "plan_feedback.html",
        plan=plan,
        feedback_type=feedback_type,
        error=error
    )


# ============================================================
# GETRENNTE PDF-DOWNLOADS
# ============================================================

@app.route(
    "/plans/<int:plan_id>/nutrition-pdf"
)
def download_nutrition_pdf(plan_id):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    from pdf_generator import (
        generate_nutrition_pdf
    )

    output_folder = "generated_pdfs"

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        output_folder,
        f"nutrition_plan_{plan.id}.pdf"
    )

    generate_nutrition_pdf(
        plan=plan,
        user=user,
        profile=profile_data,
        file_path=file_path
    )

    return send_file(
        file_path,
        as_attachment=True,
        download_name=(
            f"{plan.nutrition_title}.pdf"
        )
    )


@app.route(
    "/plans/<int:plan_id>/fitness-pdf"
)
def download_fitness_pdf(plan_id):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    from pdf_generator import (
        generate_fitness_pdf
    )

    output_folder = "generated_pdfs"

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        output_folder,
        f"fitness_plan_{plan.id}.pdf"
    )

    generate_fitness_pdf(
        plan=plan,
        user=user,
        profile=profile_data,
        file_path=file_path
    )

    return send_file(
        file_path,
        as_attachment=True,
        download_name=(
            f"{plan.fitness_title}.pdf"
        )
    )


@app.route(
    "/plans/<int:plan_id>/shopping-pdf"
)
def download_shopping_pdf(plan_id):
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    from pdf_generator import (
        generate_shopping_pdf
    )

    output_folder = "generated_pdfs"

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        output_folder,
        f"shopping_list_{plan.id}.pdf"
    )

    generate_shopping_pdf(
        plan=plan,
        user=user,
        profile=profile_data,
        file_path=file_path
    )

    return send_file(
        file_path,
        as_attachment=True,
        download_name=(
            f"{plan.shopping_title}.pdf"
        )
    )


# ============================================================
# SUPPORT FÜR BENUTZER
# ============================================================

@app.route(
    "/support",
    methods=["GET", "POST"]
)
def support():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    error = None

    if request.method == "POST":
        subject = request.form.get(
            "subject",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        message_text = request.form.get(
            "message",
            ""
        ).strip()

        if len(subject) < 3:
            error = (
                "Bitte gib einen aussagekräftigen "
                "Betreff ein."
            )

        elif len(subject) > 180:
            error = (
                "Der Betreff darf höchstens "
                "180 Zeichen lang sein."
            )

        elif category not in SUPPORT_CATEGORIES:
            error = (
                "Bitte wähle eine gültige Kategorie."
            )

        elif len(message_text) < 10:
            error = (
                "Bitte beschreibe dein Anliegen "
                "mit mindestens 10 Zeichen."
            )

        elif len(message_text) > 5000:
            error = (
                "Die Nachricht darf höchstens "
                "5.000 Zeichen lang sein."
            )

        else:
            support_message = SupportMessage(
                subject=subject,
                category=category,
                message=message_text,
                status="Offen",
                user_id=user.id
            )

            db.session.add(
                support_message
            )

            db.session.commit()

            return redirect(
                url_for(
                    "support",
                    sent="1"
                )
            )

    own_messages = (
        SupportMessage.query
        .filter_by(user_id=user.id)
        .order_by(
            SupportMessage.created_at.desc()
        )
        .all()
    )

    return render_template(
        "support.html",
        categories=SUPPORT_CATEGORIES,
        own_messages=own_messages,
        error=error
    )


# ============================================================
# ADMIN-SUPPORT
# ============================================================

@app.route(
    "/admin/support",
    methods=["GET", "POST"]
)
def admin_support():
    user = get_logged_in_user()

    if not user:
        session.clear()

        return redirect(
            url_for("login")
        )

    if not user_is_admin(user):
        abort(403)

    error = None
    success = None

    if request.method == "POST":
        message_id_text = request.form.get(
            "message_id",
            ""
        ).strip()

        new_status = request.form.get(
            "status",
            ""
        ).strip()

        admin_response = request.form.get(
            "admin_response",
            ""
        ).strip()

        try:
            message_id = int(
                message_id_text
            )

        except ValueError:
            message_id = None
            error = (
                "Die Supportnachricht konnte "
                "nicht gefunden werden."
            )

        support_message = None

        if message_id is not None:
            support_message = db.session.get(
                SupportMessage,
                message_id
            )

        if not support_message:
            error = (
                "Die Supportnachricht wurde "
                "nicht gefunden."
            )

        elif new_status not in SUPPORT_STATUS_VALUES:
            error = (
                "Bitte wähle einen gültigen Status."
            )

        elif len(admin_response) > 5000:
            error = (
                "Die Antwort darf höchstens "
                "5.000 Zeichen lang sein."
            )

        else:
            support_message.status = (
                new_status
            )

            support_message.admin_response = (
                admin_response
                or None
            )

            # Sobald eine Antwort geschrieben wurde,
            # wird der Status automatisch auf
            # "Beantwortet" gesetzt, sofern nicht
            # bewusst "Geschlossen" gewählt wurde.
            if (
                admin_response
                and new_status != "Geschlossen"
            ):
                support_message.status = (
                    "Beantwortet"
                )

            db.session.commit()

            success = (
                "Die Supportanfrage wurde aktualisiert."
            )

    selected_status = request.args.get(
        "status",
        ""
    ).strip()

    query = SupportMessage.query

    if selected_status in SUPPORT_STATUS_VALUES:
        query = query.filter_by(
            status=selected_status
        )

    support_messages = (
        query
        .order_by(
            SupportMessage.created_at.desc()
        )
        .all()
    )

    status_counts = {
        status: SupportMessage.query.filter_by(
            status=status
        ).count()
        for status in SUPPORT_STATUS_VALUES
    }

    return render_template(
        "admin_support.html",
        support_messages=support_messages,
        status_values=SUPPORT_STATUS_VALUES,
        status_counts=status_counts,
        selected_status=selected_status,
        error=error,
        success=success
    )


# ============================================================
# FEHLERSEITEN
# ============================================================

@app.errorhandler(403)
def forbidden(_error):
    return (
        render_template(
            "error.html",
            error_code=403,
            error_title="Zugriff nicht erlaubt",
            error_message=(
                "Du hast keine Berechtigung, "
                "diese Seite aufzurufen."
            )
        ),
        403
    )


@app.errorhandler(404)
def page_not_found(_error):
    return (
        render_template(
            "error.html",
            error_code=404,
            error_title="Seite nicht gefunden",
            error_message=(
                "Die gewünschte Seite oder der "
                "gewünschte Eintrag wurde nicht gefunden."
            )
        ),
        404
    )


# ============================================================
# DATENBANK UND APP-START
# ============================================================

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )