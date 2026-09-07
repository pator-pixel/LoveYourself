from flask import (
    Blueprint,
    g,
    render_template,
    request,
)

from services.support_service import (
    SupportValidationError,
    get_support_overview,
    update_support_message,
)
from utils.decorators import admin_required


admin_bp = Blueprint(
    "admin_routes",
    __name__
)


@admin_bp.route(
    "/admin/support",
    methods=["GET", "POST"]
)
@admin_required
def admin_support():
    user = g.current_user
    error = None
    success = None

    if request.method == "POST":
        message_id_text = request.form.get(
            "message_id",
            ""
        ).strip()

        try:
            message_id = int(
                message_id_text
            )

        except ValueError:
            error = (
                "Die Supportnachricht konnte "
                "nicht gefunden werden."
            )

        else:
            try:
                update_support_message(
                    message_id=message_id,
                    new_status=request.form.get(
                        "status",
                        ""
                    ),
                    admin_response=request.form.get(
                        "admin_response",
                        ""
                    ),
                )

            except SupportValidationError as validation_error:
                error = str(validation_error)

            else:
                success = (
                    "Die Supportanfrage wurde aktualisiert."
                )

    overview = get_support_overview(
        request.args.get(
            "status",
            ""
        )
    )

    return render_template(
        "admin_support.html",
        error=error,
        success=success,
        **overview
    )
