from flask_sqlalchemy import SQLAlchemy


# Die Erweiterung wird hier nur erstellt.
# Die Verbindung zur Flask-App erfolgt später in app.py
# über db.init_app(app).
db = SQLAlchemy()
