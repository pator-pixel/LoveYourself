from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from extensions import db

from models import (
    ExercisePreference,
    MealPreference,
    Plan,
    PlanFeedback,
    Profile,
)

from services.feedback_service import save_plan_feedback
from services.pdf_service import create_plan_pdf
from services.plan_generation_service import (
    PlanGenerationError,
    generate_and_save_fitness_plan,
    generate_and_save_nutrition_plan,
)

from utils.decorators import login_required
from utils.helpers import (
    join_selected_values,
    parse_json_data,
)


plans_bp = Blueprint(
    "plans_routes",
    __name__
)


# =========================================================
# HILFSFUNKTION
# =========================================================

def get_owned_plan(plan_id, user_id):
    """
    Lädt einen Plan nur für den zugehörigen Benutzer.
    """

    return Plan.query.filter_by(
        id=plan_id,
        user_id=user_id
    ).first()


# =========================================================
# PLANART AUSWÄHLEN
# =========================================================

@plans_bp.route("/generate-plan")
@login_required
def generate_plan():
    """
    Zeigt die Auswahlseite an:
    Ernährungsplan oder Fitnessplan.
    """

    return render_template(
        "generate_plan.html"
    )


# =========================================================
# ERNÄHRUNGSPLAN + EINKAUFSLISTE GENERIEREN
# =========================================================

@plans_bp.route("/generate-nutrition-plan")
@login_required
def generate_nutrition_plan():
    user = g.current_user

    try:

        plan = generate_and_save_nutrition_plan(
            user
        )

    except ValueError as error:

        if str(error) == "PROFILE_MISSING":

            return redirect(
                url_for(
                    "profile_routes.profile"
                )
            )

        if str(error) == "PROFILE_INCOMPLETE":

            return (
                "Der Ernährungsplan konnte nicht "
                "erstellt werden. Bitte fülle Alter, "
                "Geschlecht, Größe, Gewicht und "
                "Aktivitätslevel aus.",
                400
            )

        raise

    except PlanGenerationError as error:

        current_app.logger.exception(
            "Fehler bei der Erstellung "
            "des Ernährungsplans"
        )

        return (
            f"Der Ernährungsplan konnte nicht "
            f"erstellt werden. {error}",
            503
        )

    return redirect(
        url_for(
            "plans_routes.view_plan",
            plan_id=plan.id
        )
    )


# =========================================================
# FITNESSPLAN GENERIEREN
# =========================================================

@plans_bp.route("/generate-fitness-plan")
@login_required
def generate_fitness_plan():
    user = g.current_user

    try:

        plan = generate_and_save_fitness_plan(
            user
        )

    except ValueError as error:

        if str(error) == "PROFILE_MISSING":

            return redirect(
                url_for(
                    "profile_routes.profile"
                )
            )

        if str(error) == "PROFILE_INCOMPLETE":

            return (
                "Der Fitnessplan konnte nicht "
                "erstellt werden. Bitte vervollständige "
                "dein Profil.",
                400
            )

        raise

    except PlanGenerationError as error:

        current_app.logger.exception(
            "Fehler bei der Erstellung "
            "des Fitnessplans"
        )

        return (
            f"Der Fitnessplan konnte nicht "
            f"erstellt werden. {error}",
            503
        )

    return redirect(
        url_for(
            "plans_routes.view_plan",
            plan_id=plan.id
        )
    )


# =========================================================
# ALLE PLÄNE
# =========================================================

@plans_bp.route("/plans")
@login_required
def plans():
    user = g.current_user

    user_plans = (
        Plan.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            Plan.id.desc()
        )
        .all()
    )

    nutrition_plans = [
        plan
        for plan in user_plans
        if plan.plan_type == "nutrition"
    ]

    fitness_plans = [
        plan
        for plan in user_plans
        if plan.plan_type == "fitness"
    ]

    return render_template(
        "plans.html",
        plans=user_plans,
        nutrition_plans=nutrition_plans,
        fitness_plans=fitness_plans
    )


# =========================================================
# EINZELNEN PLAN ANZEIGEN
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>"
)
@login_required
def view_plan(plan_id):
    user = g.current_user

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    nutrition_days = []
    fitness_days = []
    shopping_categories = []

    # -----------------------------------------------------
    # ERNÄHRUNGSPLAN
    # -----------------------------------------------------

    if plan.plan_type == "nutrition":

        nutrition_days = parse_json_data(
            plan.nutrition_data,
            []
        )

        shopping_categories = parse_json_data(
            plan.shopping_data,
            []
        )

    # -----------------------------------------------------
    # FITNESSPLAN
    # -----------------------------------------------------

    elif plan.plan_type == "fitness":

        fitness_days = parse_json_data(
            plan.fitness_data,
            []
        )

    # -----------------------------------------------------
    # UNBEKANNTE PLANART
    # -----------------------------------------------------

    else:
        abort(404)

    # -----------------------------------------------------
    # BEWERTUNGEN LADEN
    # -----------------------------------------------------

    meal_preferences = {}
    exercise_preferences = {}


    # -----------------------------------------------------
    # GERICHTSBEWERTUNGEN
    # -----------------------------------------------------

    if plan.plan_type == "nutrition":

        stored_meal_preferences = (
            MealPreference.query
            .filter_by(
                user_id=user.id
            )
            .all()
        )

        meal_preferences = {
            preference.meal_name:
                preference.preference
            for preference
            in stored_meal_preferences
        }


    # -----------------------------------------------------
    # ÜBUNGSBEWERTUNGEN
    # -----------------------------------------------------

    elif plan.plan_type == "fitness":

        stored_exercise_preferences = (
            ExercisePreference.query
            .filter_by(
                user_id=user.id
            )
            .all()
        )

        exercise_preferences = {
            preference.exercise_name:
                preference.preference
            for preference
            in stored_exercise_preferences
        }


    existing_plan_feedback = (
        PlanFeedback.query
        .filter_by(
            user_id=user.id,
            plan_id=plan.id,
            feedback_type=plan.plan_type,
        )
        .order_by(PlanFeedback.id.desc())
        .first()
    )

    return render_template(
        "plan.html",
        plan=plan,
        user=user,
        nutrition_days=nutrition_days,
        fitness_days=fitness_days,
        shopping_categories=shopping_categories,
        meal_preferences=meal_preferences,
        exercise_preferences=exercise_preferences,
        has_plan_feedback=existing_plan_feedback is not None
    )


# =========================================================
# GERICHT BEWERTEN
# =========================================================

# =========================================================
# GERICHT BEWERTEN
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/meal-preference",
    methods=["POST"]
)
@login_required
def set_meal_preference(plan_id):
    """
    Speichert eine Gerichtspräferenz.

    like:
        Gericht bevorzugen.

    dislike:
        Gericht künftig ausschließen.

    Gleiche Bewertung erneut:
        wieder neutral.
    """

    user = g.current_user

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    if plan.plan_type != "nutrition":
        abort(400)


    meal_name = request.form.get(
        "meal_name",
        ""
    ).strip()

    preference_value = request.form.get(
        "preference",
        ""
    ).strip()


    if not meal_name:
        abort(400)

    if len(meal_name) > 200:
        abort(400)

    if preference_value not in {
        "like",
        "dislike"
    }:
        abort(400)


    existing_preference = (
        MealPreference.query
        .filter_by(
            user_id=user.id,
            meal_name=meal_name
        )
        .first()
    )


    # Standard:
    # neue Bewertung wird aktiv
    final_preference = preference_value


    if existing_preference:

        # Gleicher Daumen erneut:
        # zurück auf neutral

        if (
            existing_preference.preference
            == preference_value
        ):

            db.session.delete(
                existing_preference
            )

            final_preference = None

        # Anderen Daumen gewählt:
        # Bewertung wechseln

        else:

            existing_preference.preference = (
                preference_value
            )

            final_preference = (
                preference_value
            )

    else:

        new_preference = MealPreference(
            meal_name=meal_name,
            preference=preference_value,
            user_id=user.id
        )

        db.session.add(
            new_preference
        )


    db.session.commit()


    # JavaScript bekommt nur den neuen Zustand zurück.
    # Kein Redirect, kein Reload, kein Springen.

    return jsonify({
        "success": True,
        "meal_name": meal_name,
        "preference": final_preference
    })


# =========================================================
# ÜBUNG BEWERTEN
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/exercise-preference",
    methods=["POST"]
)
@login_required
def set_exercise_preference(plan_id):
    """
    Speichert eine Übungspräferenz.

    like:
        Übung bevorzugen.

    dislike:
        Übung künftig ausschließen.

    Gleiche Bewertung erneut:
        wieder neutral.
    """

    user = g.current_user

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    if plan.plan_type != "fitness":
        abort(400)


    # -----------------------------------------------------
    # FORMULARDATEN
    # -----------------------------------------------------

    exercise_name = request.form.get(
        "exercise_name",
        ""
    ).strip()

    preference_value = request.form.get(
        "preference",
        ""
    ).strip()


    # -----------------------------------------------------
    # VALIDIERUNG
    # -----------------------------------------------------

    if not exercise_name:
        abort(400)

    if len(exercise_name) > 200:
        abort(400)

    if preference_value not in {
        "like",
        "dislike"
    }:
        abort(400)


    # -----------------------------------------------------
    # VORHANDENE BEWERTUNG
    # -----------------------------------------------------

    existing_preference = (
        ExercisePreference.query
        .filter_by(
            user_id=user.id,
            exercise_name=exercise_name
        )
        .first()
    )

    final_preference = preference_value


    # -----------------------------------------------------
    # BEWERTUNG ÄNDERN
    # -----------------------------------------------------

    if existing_preference:

        if (
            existing_preference.preference
            == preference_value
        ):

            db.session.delete(
                existing_preference
            )

            final_preference = None

        else:

            existing_preference.preference = (
                preference_value
            )

            final_preference = (
                preference_value
            )

    else:

        new_preference = ExercisePreference(
            exercise_name=exercise_name,
            preference=preference_value,
            user_id=user.id
        )

        db.session.add(
            new_preference
        )


    db.session.commit()


    # -----------------------------------------------------
    # AJAX-ANTWORT
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "exercise_name": exercise_name,
        "preference": final_preference
    })


# =========================================================
# FEEDBACK
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/feedback/<feedback_type>",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def plan_feedback(
    plan_id,
    feedback_type
):
    user = g.current_user

    # -----------------------------------------------------
    # NUR ERLAUBTE FEEDBACK-TYPEN
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # FALSCHE FEEDBACK-KOMBINATION VERHINDERN
    # -----------------------------------------------------

    if (
        feedback_type == "nutrition"
        and plan.plan_type != "nutrition"
    ):
        abort(400)

    if (
        feedback_type == "fitness"
        and plan.plan_type != "fitness"
    ):
        abort(400)

    # -----------------------------------------------------
    # PROFIL LADEN
    # -----------------------------------------------------

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:

        return redirect(
            url_for(
                "profile_routes.profile"
            )
        )

    error = None

    existing_feedback = (
        PlanFeedback.query
        .filter_by(
            user_id=user.id,
            plan_id=plan.id,
            feedback_type=feedback_type,
        )
        .order_by(PlanFeedback.id.desc())
        .first()
    )

    # -----------------------------------------------------
    # FEEDBACK SPEICHERN
    # -----------------------------------------------------

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

        if not error:

            save_plan_feedback(
                user=user,
                plan=plan,
                profile=profile,
                feedback_type=feedback_type,
                rating=rating,

                liked_items=request.form.get(
                    "liked_items",
                    ""
                ).strip(),

                disliked_items=request.form.get(
                    "disliked_items",
                    ""
                ).strip(),

                favorite_meals=request.form.get(
                    "favorite_meals",
                    ""
                ).strip(),

                selected_preferences=(
                    join_selected_values(
                        request.form.getlist(
                            "selected_preferences"
                        )
                    )
                ),

                preferred_training_duration=(
                    request.form.get(
                        "preferred_training_duration",
                        ""
                    ).strip()
                ),

                wishes=request.form.get(
                    "wishes",
                    ""
                ).strip(),

                comment=request.form.get(
                    "comment",
                    ""
                ).strip(),
                existing_feedback=existing_feedback,
            )

            return redirect(
                url_for(
                    "plans_routes.view_plan",
                    plan_id=plan.id,
                    feedback_saved="1"
                )
            )

    return render_template(
        "plan_feedback.html",
        plan=plan,
        feedback_type=feedback_type,
        error=error,
        feedback=existing_feedback,
        selected_feedback_preferences=(
            existing_feedback.selected_preferences.splitlines()
            if existing_feedback and existing_feedback.selected_preferences
            else []
        )
    )


# =========================================================
# PDF-HILFSFUNKTION
# =========================================================

def _download_plan_pdf(
    plan_id,
    pdf_type
):
    user = g.current_user

    # -----------------------------------------------------
    # PLAN LADEN
    # -----------------------------------------------------

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    # -----------------------------------------------------
    # NUR PASSENDE PDF-TYPEN ERLAUBEN
    # -----------------------------------------------------

    if pdf_type in {
        "nutrition",
        "shopping"
    }:

        if plan.plan_type != "nutrition":
            abort(404)

    elif pdf_type == "fitness":

        if plan.plan_type != "fitness":
            abort(404)

    else:
        abort(400)

    # -----------------------------------------------------
    # PROFIL LADEN
    # -----------------------------------------------------

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    # -----------------------------------------------------
    # DURCHGESTRICHENE EINKAUFSARTIKEL
    #
    # Beispiel:
    #
    # /shopping-pdf?exclude=Banane&exclude=Haferflocken
    #
    # Diese Lebensmittel werden in der aktualisierten
    # Einkaufsliste nicht mehr ausgegeben.
    # -----------------------------------------------------

    excluded_items = []

    if pdf_type == "shopping":

        excluded_items = request.args.getlist(
            "exclude"
        )

    # -----------------------------------------------------
    # PDF ERSTELLEN
    # -----------------------------------------------------

    file_path, download_name = create_plan_pdf(
        pdf_type=pdf_type,
        plan=plan,
        user=user,
        profile=profile,
        excluded_items=excluded_items
    )

    return send_file(
        file_path,
        as_attachment=True,
        download_name=download_name
    )


# =========================================================
# ERNÄHRUNGSPLAN PDF
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/nutrition-pdf"
)
@login_required
def download_nutrition_pdf(
    plan_id
):

    return _download_plan_pdf(
        plan_id,
        "nutrition"
    )


# =========================================================
# FITNESSPLAN PDF
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/fitness-pdf"
)
@login_required
def download_fitness_pdf(
    plan_id
):

    return _download_plan_pdf(
        plan_id,
        "fitness"
    )


# =========================================================
# EINKAUFSLISTE PDF
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/shopping-pdf"
)
@login_required
def download_shopping_pdf(
    plan_id
):

    return _download_plan_pdf(
        plan_id,
        "shopping"
    )

# =========================================================
# PLAN LÖSCHEN
# =========================================================

@plans_bp.route(
    "/plans/<int:plan_id>/delete",
    methods=["POST"]
)
@login_required
def delete_plan(plan_id):
    """
    Löscht einen Plan nur dann,
    wenn er dem eingeloggten Benutzer gehört.
    """

    user = g.current_user

    plan = get_owned_plan(
        plan_id,
        user.id
    )

    if not plan:
        abort(404)

    db.session.delete(
        plan
    )

    db.session.commit()

    return redirect(
        url_for(
            "plans_routes.plans"
        )
    )