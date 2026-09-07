from flask import render_template


def register_error_handlers(app):
    """Registriert gemeinsame Fehlerseiten."""

    @app.errorhandler(403)
    def forbidden(_error):
        return (
            render_template(
                "error.html",
                error_code=403,
                error_title="Zugriff nicht erlaubt",
                error_message=(
                    "Du hast keine Berechtigung, "
                    "diese Seite aufzurufen."
                ),
            ),
            403,
        )

    @app.errorhandler(404)
    def page_not_found(_error):
        return (
            render_template(
                "error.html",
                error_code=404,
                error_title="Seite nicht gefunden",
                error_message=(
                    "Die gewünschte Seite oder der "
                    "gewünschte Eintrag wurde nicht gefunden."
                ),
            ),
            404,
        )
