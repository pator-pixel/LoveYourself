from datetime import datetime

from extensions import db


class SupportMessage(db.Model):
    __tablename__ = "support_message"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="Offen"
    )
    admin_response = db.Column(db.Text)
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
