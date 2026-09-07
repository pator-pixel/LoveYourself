import random

from flask import Blueprint, g, render_template

from utils.decorators import login_required
from services.dashboard_service import build_dashboard_data
from utils.constants import LOVE_MESSAGES_DE


dashboard_bp = Blueprint(
    "dashboard_routes",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = g.current_user

    dashboard_data = build_dashboard_data(
        user
    )

    return render_template(
        "dashboard.html",
        message=random.choice(
            LOVE_MESSAGES_DE
        ),
        **dashboard_data
    )
