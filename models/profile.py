from extensions import db


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)

    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    goal_weight = db.Column(db.Float)
    activity_level = db.Column(db.String(50))

    diet_type = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    diseases = db.Column(db.Text)
    limitations = db.Column(db.Text)
    liked_foods = db.Column(db.Text)
    disliked_foods = db.Column(db.Text)
    favorite_meals = db.Column(db.Text)
    nutrition_wishes = db.Column(db.Text)
    nutrition_notes = db.Column(db.Text)

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
    preferred_training_time = db.Column(db.String(50))
    fitness_notes = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )
