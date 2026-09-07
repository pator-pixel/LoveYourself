from app import create_app
from extensions import db
from models import User, Plan

app = create_app()

with app.app_context():
    # Zuerst Pläne löschen
    Plan.query.delete()

    # Danach Benutzer löschen
    User.query.delete()

    db.session.commit()

    print("Alle Benutzer sowie Ernährungs- und Fitnesspläne wurden gelöscht.")