"""Sign-in, logout, and route protection tests."""

from werkzeug.security import check_password_hash

from app.auth import admin_password_hash, verify_admin
from tests.conftest import csrf_from


def test_admin_password_is_hashed():
    hashed = admin_password_hash()
    assert hashed != "admin"
    assert check_password_hash(hashed, "admin")
    assert verify_admin("admin", "admin")
    assert not verify_admin("admin", "wrong")
    assert not verify_admin("other", "admin")


def test_login_success(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("user") == "admin"


def test_login_failure(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "nope"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    with client.session_transaction() as sess:
        assert sess.get("user") is None


def test_protected_redirect(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout(auth_client):
    token = csrf_from(auth_client)
    response = auth_client.post(
        "/logout",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    with auth_client.session_transaction() as sess:
        assert sess.get("user") is None


def test_session_cookie_httponly(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
