from services.auth_service import (
    get_logged_in_user,
    user_is_admin,
)


def register_context_processors(app):
    """Registriert globale Template-Werte."""

    @app.context_processor
    def inject_navigation_state():
        current_user = get_logged_in_user()

        return {
            "current_user": current_user,
            "is_logged_in": current_user is not None,
            "is_admin": user_is_admin(current_user),
        }
