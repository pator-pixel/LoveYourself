from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.account_service import (
    AccountValidationError,
    authenticate_user,
    create_temporary_password,
    register_user,
    update_password,
)
from utils.decorators import login_required


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():
    error = None

    if request.method == "POST":
        try:
            register_user(
                username=request.form.get(
                    "username",
                    ""
                ),
                password=request.form.get(
                    "password",
                    ""
                ),
                confirm_password=request.form.get(
                    "confirm_password",
                    ""
                ),
                language=request.form.get(
                    "language",
                    "de"
                ),
            )

        except AccountValidationError as validation_error:
            error = str(validation_error)

        else:
            return redirect(
                url_for("auth.login")
            )

    return render_template(
        "register.html",
        error=error
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    error = None

    if request.method == "POST":
        user = authenticate_user(
            request.form.get(
                "username",
                ""
            ),
            request.form.get(
                "password",
                ""
            ),
        )

        if user:
            session.clear()
            session["user_id"] = user.id

            return redirect(
                url_for(
                    "dashboard_routes.dashboard"
                )
            )

        error = (
            "Benutzername oder Passwort ist falsch."
        )

    return render_template(
        "login.html",
        error=error
    )


@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():
    temporary_password = None
    error = None

    if request.method == "POST":
        try:
            temporary_password = create_temporary_password(
                request.form.get(
                    "username",
                    ""
                )
            )

        except AccountValidationError as validation_error:
            error = str(validation_error)

    return render_template(
        "forgot_password.html",
        error=error,
        temporary_password=temporary_password
    )


@auth_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
@login_required
def change_password():
    user = g.current_user

    error = None
    success = None

    if request.method == "POST":
        try:
            update_password(
                user=user,
                current_password=request.form.get(
                    "current_password",
                    ""
                ),
                new_password=request.form.get(
                    "new_password",
                    ""
                ),
                confirm_password=request.form.get(
                    "confirm_password",
                    ""
                ),
            )

        except AccountValidationError as validation_error:
            error = str(validation_error)

        else:
            success = (
                "Dein Passwort wurde erfolgreich geändert."
            )

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


@auth_bp.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("public.index")
    )
