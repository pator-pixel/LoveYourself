LEGACY_URL_ALIASES = [
    ("/", "index"),
    ("/about", "about"),
    ("/impressum", "impressum"),
    ("/register", "register"),
    ("/login", "login"),
    ("/forgot-password", "forgot_password"),
    ("/change-password", "change_password"),
    ("/logout", "logout"),
    ("/dashboard", "dashboard"),
    ("/profile", "profile"),
    ("/profile-view", "profile_view"),
    ("/weight", "weight_tracking"),
    (
        "/weight/<int:entry_id>/delete",
        "delete_weight_entry"
    ),
    ("/generate-plan", "generate_plan"),
    ("/plans", "plans"),
    ("/plans/<int:plan_id>", "view_plan"),
    (
        "/plans/<int:plan_id>/feedback/<feedback_type>",
        "plan_feedback"
    ),
    (
        "/plans/<int:plan_id>/nutrition-pdf",
        "download_nutrition_pdf"
    ),
    (
        "/plans/<int:plan_id>/fitness-pdf",
        "download_fitness_pdf"
    ),
    (
        "/plans/<int:plan_id>/shopping-pdf",
        "download_shopping_pdf"
    ),
    ("/support", "support"),
    ("/admin/support", "admin_support"),
]


def register_legacy_url_aliases(app):
    """
    Hält alte url_for()-Aufrufe vorübergehend kompatibel.

    Nach der Umstellung aller Templates auf Blueprint-Endpunkte
    kann dieses Modul entfernt werden.
    """

    for rule, endpoint in LEGACY_URL_ALIASES:
        app.add_url_rule(
            rule,
            endpoint=endpoint,
            build_only=True
        )
