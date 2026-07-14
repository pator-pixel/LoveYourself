from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    language = db.Column(
        db.String(10),
        nullable=False,
        default="de"
    )

    profile = db.relationship(
        "Profile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    weight_entries = db.relationship(
        "WeightEntry",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    plans = db.relationship(
        "Plan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    feedback_entries = db.relationship(
        "PlanFeedback",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    support_messages = db.relationship(
        "SupportMessage",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Persönliche Daten
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Float)

    # Das Feld weight bleibt dauerhaft das Startgewicht.
    weight = db.Column(db.Float)
    goal_weight = db.Column(db.Float)

    activity_level = db.Column(db.String(50))

    # Ernährung
    diet_type = db.Column(db.String(50))

    allergies = db.Column(db.Text)
    diseases = db.Column(db.Text)
    limitations = db.Column(db.Text)

    liked_foods = db.Column(db.Text)
    disliked_foods = db.Column(db.Text)
    favorite_meals = db.Column(db.Text)
    nutrition_wishes = db.Column(db.Text)

    # Alte Felder bleiben zunächst bestehen,
    # werden aber nicht mehr in der Profilseite verwendet.
    nutrition_notes = db.Column(db.Text)

    # Training
    fitness_level = db.Column(db.String(50))
    training_days = db.Column(db.Integer)

    has_gym = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    home_equipment = db.Column(db.Text)

    liked_exercises = db.Column(db.Text)
    disliked_exercises = db.Column(db.Text)

    preferred_training_types = db.Column(db.Text)
    preferred_training_duration = db.Column(db.String(50))
    fitness_wishes = db.Column(db.Text)

    # Wird in der vereinfachten Version nicht mehr verwendet.
    preferred_training_time = db.Column(db.String(50))
    fitness_notes = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )


class WeightEntry(db.Model):
    __tablename__ = "weight_entry"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    weight = db.Column(
        db.Float,
        nullable=False
    )

    date = db.Column(
        db.String(20),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Plan(db.Model):
    __tablename__ = "plan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nutrition_title = db.Column(
        db.String(160),
        nullable=False
    )

    fitness_title = db.Column(
        db.String(160),
        nullable=False
    )

    shopping_title = db.Column(
        db.String(160),
        nullable=False
    )

    created_at = db.Column(
        db.String(20),
        nullable=False
    )

    current_weight = db.Column(db.Float)
    calories = db.Column(db.Integer)

    # Profildaten zum Zeitpunkt der Erstellung.
    allergies_snapshot = db.Column(db.Text)
    excluded_foods_snapshot = db.Column(db.Text)

    # An die AI gesendete Prompts.
    nutrition_prompt = db.Column(db.Text)
    fitness_prompt = db.Column(db.Text)

    # Strukturierte JSON-Daten.
    nutrition_data = db.Column(
        db.Text,
        nullable=False
    )

    fitness_data = db.Column(
        db.Text,
        nullable=False
    )

    shopping_data = db.Column(
        db.Text,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    feedback_entries = db.relationship(
        "PlanFeedback",
        backref="plan",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def title(self):
        return f"Pläne vom {self.created_at}"


class PlanFeedback(db.Model):
    __tablename__ = "plan_feedback"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # nutrition oder fitness
    feedback_type = db.Column(
        db.String(20),
        nullable=False
    )

    rating = db.Column(db.Integer)

    liked_items = db.Column(db.Text)
    disliked_items = db.Column(db.Text)
    favorite_meals = db.Column(db.Text)

    selected_preferences = db.Column(db.Text)
    preferred_training_duration = db.Column(db.String(50))

    # Bleibt aus Kompatibilitätsgründen erhalten.
    preferred_training_time = db.Column(db.String(50))

    wishes = db.Column(db.Text)
    comment = db.Column(db.Text)

    created_at = db.Column(
        db.String(20),
        nullable=False
    )

    plan_id = db.Column(
        db.Integer,
        db.ForeignKey("plan.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class SupportMessage(db.Model):
    __tablename__ = "support_message"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    subject = db.Column(
        db.String(180),
        nullable=False
    )

    category = db.Column(
        db.String(80),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Offen"
    )

    admin_response = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    @property
    def formatted_created_at(self):
        if not self.created_at:
            return "Nicht angegeben"

        return self.created_at.strftime(
            "%d.%m.%Y um %H:%M Uhr"
        )

    @property
    def formatted_updated_at(self):
        if not self.updated_at:
            return "Nicht angegeben"

        return self.updated_at.strftime(
            "%d.%m.%Y um %H:%M Uhr"
        )