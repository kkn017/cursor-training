"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    registry = tmp_path / "servers.json"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "REGISTRY_PATH": str(registry),
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    client.post("/login", data={"username": "admin", "password": "admin"})
    return client


def csrf_from(client):
    """Pull CSRF token from session after a logged-in page load."""
    with client.session_transaction() as sess:
        return sess.get("_csrf_token")
