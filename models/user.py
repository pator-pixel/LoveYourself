from extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
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
