import random
import string
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Profile, WeightEntry


app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///love_yourself.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


LOVE_MESSAGES_DE = [
    "Es ist nicht schlimm, wenn du heute einen schlechten Tag hattest. Morgen ist eine neue Chance. Denk daran: Love Yourself.",
    "Perfektion ist nicht das Ziel. Beständigkeit ist wichtiger als ein einzelner perfekter Tag.",
    "Ein Spaziergang von 20 Minuten ist besser als gar keine Bewegung. Jeder Schritt zählt.",
    "Schlaf ist kein Luxus. Er ist ein wichtiger Teil deiner Gesundheit. Versuche heute 7 bis 9 Stunden zu schlafen.",
    "Du arbeitest an deiner Gesundheit, nicht an deinem Wert als Mensch. Du bist jetzt schon wertvoll."
]


def is_valid_password(password):
    if len(password) < 8:
        return False

    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in string.punctuation for char in password)

    return has_uppercase and has_lowercase and has_digit and has_special


def generate_temporary_password():
    return "Love" + "".join(
        random.choices(string.ascii_letters + string.digits, k=8)
    ) + "!"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        language = request.form.get("language", "de")

        if not username or len(username) < 3:
            error = "Der Benutzername muss mindestens 3 Zeichen lang sein."
            return render_template("register.html", error=error)

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            error = "Dieser Benutzername ist bereits vergeben."
            return render_template("register.html", error=error)

        if password != confirm_password:
            error = "Die Passwörter stimmen nicht überein."
            return render_template("register.html", error=error)

        if not is_valid_password(password):
            error = (
                "Das Passwort muss mindestens 8 Zeichen, einen Großbuchstaben, "
                "einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten."
            )
            return render_template("register.html", error=error)

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            language=language
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    temporary_password = None
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()

        if not user:
            error = "Dieser Benutzername wurde nicht gefunden."
            return render_template(
                "forgot_password.html",
                error=error,
                temporary_password=temporary_password
            )

        temporary_password = generate_temporary_password()
        user.password_hash = generate_password_hash(temporary_password)
        db.session.commit()

    return render_template(
        "forgot_password.html",
        error=error,
        temporary_password=temporary_password
    )


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    error = None
    success = None

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(user.password_hash, current_password):
            error = "Das aktuelle Passwort ist falsch."
            return render_template(
                "change_password.html",
                error=error,
                success=success
            )

        if new_password != confirm_password:
            error = "Die neuen Passwörter stimmen nicht überein."
            return render_template(
                "change_password.html",
                error=error,
                success=success
            )

        if not is_valid_password(new_password):
            error = (
                "Das neue Passwort muss mindestens 8 Zeichen, einen Großbuchstaben, "
                "einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten."
            )
            return render_template(
                "change_password.html",
                error=error,
                success=success
            )

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        success = "Dein Passwort wurde erfolgreich geändert."

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        error = "Benutzername oder Passwort ist falsch."
        return render_template("login.html", error=error)

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()

    entries = (
        WeightEntry.query
        .filter_by(user_id=user_id)
        .order_by(WeightEntry.id.asc())
        .all()
    )

    current_weight = None
    goal_weight = None
    remaining_weight = None
    start_weight = None
    lost_weight = None
    progress_percent = None

    if profile:
        current_weight = profile.weight
        goal_weight = profile.goal_weight

    if entries:
        start_weight = entries[0].weight
    elif current_weight:
        start_weight = current_weight

    if current_weight and goal_weight:
        remaining_weight = round(current_weight - goal_weight, 1)

    if start_weight and current_weight:
        lost_weight = round(start_weight - current_weight, 1)

    if start_weight and current_weight and goal_weight:
        total_goal = start_weight - goal_weight
        current_progress = start_weight - current_weight

        if total_goal > 0:
            progress_percent = round((current_progress / total_goal) * 100)
            progress_percent = max(0, min(progress_percent, 100))

    message = random.choice(LOVE_MESSAGES_DE)

    return render_template(
        "dashboard.html",
        user=user,
        message=message,
        current_weight=current_weight,
        goal_weight=goal_weight,
        remaining_weight=remaining_weight,
        start_weight=start_weight,
        lost_weight=lost_weight,
        progress_percent=progress_percent,
        total_entries=len(entries)
    )


@app.route("/profile-view")
def profile_view():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()

    return render_template(
        "profile_view.html",
        user=user,
        profile=profile
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    error = None

    if request.method == "POST":
        training_days_value = request.form.get("training_days")

        if training_days_value:
            training_days = int(training_days_value)
            if training_days < 1 or training_days > 7:
                error = "Trainingstage müssen zwischen 1 und 7 liegen."
                return render_template(
                    "profile.html",
                    user=user,
                    profile=profile,
                    error=error
                )
        else:
            training_days = None

        if profile is None:
            profile = Profile(user_id=user_id)
            db.session.add(profile)

        profile.age = int(request.form.get("age")) if request.form.get("age") else None
        profile.gender = request.form.get("gender")
        profile.height = float(request.form.get("height")) if request.form.get("height") else None
        profile.weight = float(request.form.get("weight")) if request.form.get("weight") else None
        profile.goal_weight = float(request.form.get("goal_weight")) if request.form.get("goal_weight") else None

        profile.diet_type = request.form.get("diet_type")

        profile.allergies = "\n".join(
            item for item in request.form.getlist("allergies_item") if item.strip()
        )

        profile.diseases = "\n".join(
            item for item in request.form.getlist("diseases_item") if item.strip()
        )

        profile.limitations = "\n".join(
            item for item in request.form.getlist("limitations_item") if item.strip()
        )

        profile.liked_foods = "\n".join(
            item for item in request.form.getlist("liked_foods_item") if item.strip()
        )

        profile.disliked_foods = "\n".join(
            item for item in request.form.getlist("disliked_foods_item") if item.strip()
        )

        profile.fitness_level = request.form.get("fitness_level")
        profile.training_days = training_days
        profile.has_gym = request.form.get("has_gym") == "yes"

        profile.home_equipment = "\n".join(
            item for item in request.form.getlist("home_equipment_item") if item.strip()
        )

        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("profile.html", user=user, profile=profile, error=error)


@app.route("/weight", methods=["GET", "POST"])
def weight_tracking():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        weight = request.form.get("weight")
        entry_date = request.form.get("date")

        if weight:
            new_entry = WeightEntry(
                weight=float(weight),
                date=entry_date if entry_date else str(date.today()),
                user_id=user_id
            )

            db.session.add(new_entry)

            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                profile.weight = float(weight)

            db.session.commit()

        return redirect(url_for("weight_tracking"))

    entries = (
        WeightEntry.query
        .filter_by(user_id=user_id)
        .order_by(WeightEntry.id.desc())
        .all()
    )

    return render_template("weight.html", entries=entries)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)