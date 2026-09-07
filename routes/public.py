import random

from flask import Blueprint, render_template

from utils.constants import LOVE_MESSAGES_DE


public_bp = Blueprint(
    "public",
    __name__
)


@public_bp.route("/")
def index():
    return render_template(
        "home.html",
        message=random.choice(LOVE_MESSAGES_DE)
    )


@public_bp.route("/about")
def about():
    """
    Die Seite:
    Die Idee hinter Love Yourself
    """

    return render_template(
        "about.html"
    )


@public_bp.route("/impressum")
def impressum():
    return render_template(
        "impressum.html"
    )
