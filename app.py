from flask import Flask

from config import Config
from context_processors import register_context_processors
from error_handlers import register_error_handlers
from extensions import db
from legacy_urls import register_legacy_url_aliases
from routes import register_blueprints


def create_app(test_config=None):
    """Erstellt und konfiguriert die Flask-Anwendung."""

    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    register_blueprints(app)
    register_legacy_url_aliases(app)
    register_context_processors(app)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )