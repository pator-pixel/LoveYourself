from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.community import community_bp
from routes.dashboard import dashboard_bp
from routes.plans import plans_bp
from routes.profile import profile_bp
from routes.public import public_bp
from routes.support import support_bp
from routes.weight import weight_bp


def register_blueprints(app):
    """Registriert alle Blueprints der Anwendung."""

    app.register_blueprint(public_bp)

    app.register_blueprint(auth_bp)

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        community_bp
    )

    app.register_blueprint(
        profile_bp
    )

    app.register_blueprint(
        weight_bp
    )

    app.register_blueprint(
        plans_bp
    )

    app.register_blueprint(
        support_bp
    )

    app.register_blueprint(
        admin_bp
    )