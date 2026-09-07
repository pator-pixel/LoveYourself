from sqlalchemy import text

from app import create_app
from extensions import db


app = create_app()


with app.app_context():

    # =====================================================
    # ALTE TABELLEN DIREKT PER SQL PRÜFEN
    # =====================================================

    plan_count = db.session.execute(
        text(
            'SELECT COUNT(*) FROM "plan"'
        )
    ).scalar()

    feedback_count = db.session.execute(
        text(
            'SELECT COUNT(*) FROM "plan_feedback"'
        )
    ).scalar()


    print(
        f"Gespeicherte Pläne: {plan_count}"
    )

    print(
        f"Gespeicherte Feedback-Einträge: {feedback_count}"
    )


    # =====================================================
    # SICHERHEIT
    # =====================================================

    if plan_count != 0 or feedback_count != 0:

        raise RuntimeError(
            "Abbruch: Es befinden sich bereits Pläne "
            "oder Feedback-Einträge in der Datenbank."
        )


    # =====================================================
    # ALTE TABELLEN LÖSCHEN
    # =====================================================

    db.session.execute(
        text(
            'DROP TABLE IF EXISTS "plan_feedback"'
        )
    )

    db.session.execute(
        text(
            'DROP TABLE IF EXISTS "plan"'
        )
    )

    db.session.commit()


    # =====================================================
    # TABELLEN NACH NEUEM MODEL ERSTELLEN
    # =====================================================

    db.create_all()


    print(
        "Plan-Tabellen wurden erfolgreich neu erstellt."
    )