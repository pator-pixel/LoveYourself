from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from models import Profile
from services.profile_service import (
    ProfileValidationError,
    save_profile_from_form,
)
from utils.decorators import login_required


profile_bp = Blueprint(
    "profile_routes",
    __name__
)


@profile_bp.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():
    user = g.current_user

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    error = None

    if request.method == "POST":
        try:
            profile_data = save_profile_from_form(
                user,
                request.form
            )

        except ProfileValidationError as validation_error:
            error = str(validation_error)

        else:
            return redirect(
                url_for(
                    "profile_routes.profile",
                    saved="1"
                )
            )

    return render_template(
        "profile.html",
        user=user,
        profile=profile_data,
        error=error
    )


@profile_bp.route("/profile-view")
@login_required
def profile_view():
    user = g.current_user

    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    return render_template(
        "profile_view.html",
        user=user,
        profile=profile_data
    )
