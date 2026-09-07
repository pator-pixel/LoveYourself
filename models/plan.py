from extensions import db


class Plan(db.Model):
    __tablename__ = "plan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # PLANART
    #
    # nutrition = Ernährungsplan + Einkaufsliste
    # fitness   = Fitnessplan
    # =====================================================

    plan_type = db.Column(
        db.String(20),
        nullable=False
    )

    # =====================================================
    # TITEL
    # =====================================================

    nutrition_title = db.Column(
        db.String(160),
        nullable=True
    )

    fitness_title = db.Column(
        db.String(160),
        nullable=True
    )

    shopping_title = db.Column(
        db.String(160),
        nullable=True
    )

    # =====================================================
    # ALLGEMEINE DATEN
    # =====================================================

    created_at = db.Column(
        db.String(20),
        nullable=False
    )

    current_weight = db.Column(
        db.Float
    )

    calories = db.Column(
        db.Integer
    )

    # =====================================================
    # SNAPSHOTS
    # =====================================================

    allergies_snapshot = db.Column(
        db.Text
    )

    excluded_foods_snapshot = db.Column(
        db.Text
    )

    # =====================================================
    # AI-PROMPTS
    # =====================================================

    nutrition_prompt = db.Column(
        db.Text
    )

    fitness_prompt = db.Column(
        db.Text
    )

    # =====================================================
    # PLAN-DATEN
    #
    # Bei einem Ernährungsplan:
    #   nutrition_data + shopping_data
    #
    # Bei einem Fitnessplan:
    #   fitness_data
    # =====================================================

    nutrition_data = db.Column(
        db.Text,
        nullable=True
    )

    fitness_data = db.Column(
        db.Text,
        nullable=True
    )

    shopping_data = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # BENUTZER
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    # =====================================================
    # FEEDBACK
    # =====================================================

    feedback_entries = db.relationship(
        "PlanFeedback",
        backref="plan",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # =====================================================
    # HILFSEIGENSCHAFTEN
    # =====================================================

    @property
    def is_nutrition_plan(self):
        return self.plan_type == "nutrition"

    @property
    def is_fitness_plan(self):
        return self.plan_type == "fitness"

    @property
    def title(self):

        if self.is_nutrition_plan:
            return (
                self.nutrition_title
                or f"Ernährungsplan vom {self.created_at}"
            )

        if self.is_fitness_plan:
            return (
                self.fitness_title
                or f"Fitnessplan vom {self.created_at}"
            )

        return f"Plan vom {self.created_at}"


class PlanFeedback(db.Model):
    __tablename__ = "plan_feedback"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    feedback_type = db.Column(
        db.String(20),
        nullable=False
    )

    rating = db.Column(
        db.Integer
    )

    liked_items = db.Column(
        db.Text
    )

    disliked_items = db.Column(
        db.Text
    )

    favorite_meals = db.Column(
        db.Text
    )

    selected_preferences = db.Column(
        db.Text
    )

    preferred_training_duration = db.Column(
        db.String(50)
    )

    preferred_training_time = db.Column(
        db.String(50)
    )

    wishes = db.Column(
        db.Text
    )

    comment = db.Column(
        db.Text
    )

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