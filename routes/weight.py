from datetime import date

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from services.weight_service import (
    WeightValidationError,
    create_weight_entry,
    delete_weight_entry_for_user,
    get_weight_entries,
)
from utils.decorators import login_required


weight_bp = Blueprint(
    "weight_routes",
    __name__
)


@weight_bp.route(
    "/weight",
    methods=["GET", "POST"]
)
@login_required
def weight_tracking():
    user = g.current_user
    error = None

    if request.method == "POST":
        try:
            create_weight_entry(
                user_id=user.id,
                weight_text=request.form.get(
                    "weight",
                    ""
                ),
                entry_date=request.form.get(
                    "date",
                    ""
                ),
            )

        except WeightValidationError as validation_error:
            error = str(validation_error)

        else:
            return redirect(
                url_for(
                    "weight_routes.weight_tracking"
                )
            )

    return render_template(
        "weight.html",
        entries=get_weight_entries(
            user.id
        ),
        today=date.today().isoformat(),
        error=error
    )


@weight_bp.route(
    "/weight/<int:entry_id>/delete",
    methods=["POST"]
)
@login_required
def delete_weight_entry(entry_id):
    user = g.current_user

    delete_weight_entry_for_user(
        entry_id=entry_id,
        user_id=user.id
    )

    return redirect(
        url_for(
            "weight_routes.weight_tracking"
        )
    )
