from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(10), default="de")

    profile = db.relationship("Profile", backref="user", uselist=False)
    weight_entries = db.relationship("WeightEntry", backref="user", lazy=True)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    goal_weight = db.Column(db.Float)

    diet_type = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    diseases = db.Column(db.Text)
    limitations = db.Column(db.Text)

    liked_foods = db.Column(db.Text)
    disliked_foods = db.Column(db.Text)

    fitness_level = db.Column(db.String(50))
    training_days = db.Column(db.Integer)
    has_gym = db.Column(db.Boolean, default=False)
    home_equipment = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)