"""Einfache Integrationstests für öffentliche und geschützte Seiten."""


def test_home_page_is_available(client):
    response = client.get("/")

    assert response.status_code == 200


def test_dashboard_redirects_anonymous_user_to_login(client):
    response = client.get("/dashboard", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert "/login" in response.headers["Location"]


def test_unknown_page_uses_404_handler(client):
    response = client.get("/diese-seite-gibt-es-nicht")

    assert response.status_code == 404
