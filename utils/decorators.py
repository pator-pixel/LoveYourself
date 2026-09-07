from functools import wraps

from flask import abort, g, redirect, session, url_for

from services.auth_service import (
    get_logged_in_user,
    user_is_admin,
)


def login_required(view_function):
    """
    Schützt eine Route vor nicht angemeldeten Zugriffen.

    Der geladene Benutzer steht innerhalb der Route über
    `g.current_user` zur Verfügung.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user = get_logged_in_user()

        if not user:
            session.clear()

            return redirect(
                url_for("auth.login")
            )

        g.current_user = user

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view


def admin_required(view_function):
    """
    Erlaubt den Zugriff nur dem konfigurierten Administrator.

    Nicht angemeldete Benutzer werden zum Login weitergeleitet.
    Angemeldete Benutzer ohne Adminrechte erhalten HTTP 403.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user = get_logged_in_user()

        if not user:
            session.clear()

            return redirect(
                url_for("auth.login")
            )

        if not user_is_admin(user):
            abort(403)

        g.current_user = user

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view
