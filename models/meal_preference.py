from extensions import db


class MealPreference(db.Model):
    __tablename__ = "meal_preference"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    meal_name = db.Column(
        db.String(200),
        nullable=False
    )

    # like    = bevorzugen
    # dislike = künftig ausschließen
    preference = db.Column(
        db.String(20),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "meal_name",
            name="uq_meal_preference_user_meal"
        ),
    )