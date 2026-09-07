from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from services.support_service import (
    SupportValidationError,
    create_support_message,
    get_user_support_messages,
)
from utils.constants import SUPPORT_CATEGORIES
from utils.decorators import login_required


support_bp = Blueprint(
    "support_routes",
    __name__
)


@support_bp.route(
    "/support",
    methods=["GET", "POST"]
)
@login_required
def support():
    user = g.current_user
    error = None

    if request.method == "POST":
        try:
            create_support_message(
                user=user,
                subject=request.form.get(
                    "subject",
                    ""
                ),
                category=request.form.get(
                    "category",
                    ""
                ),
                message_text=request.form.get(
                    "message",
                    ""
                ),
            )

        except SupportValidationError as validation_error:
            error = str(validation_error)

        else:
            return redirect(
                url_for(
                    "support_routes.support",
                    sent="1"
                )
            )

    return render_template(
        "support.html",
        categories=SUPPORT_CATEGORIES,
        own_messages=get_user_support_messages(
            user.id
        ),
        error=error
    )
