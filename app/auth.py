"""Admin sign-in helpers — hashed password only."""

from __future__ import annotations

import os
from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

ADMIN_USERNAME = "admin"

# Default demo password is "admin". Override via ADMIN_PASSWORD_HASH or ADMIN_PASSWORD.
_DEFAULT_HASH = generate_password_hash("admin")


def admin_password_hash() -> str:
    explicit = os.environ.get("ADMIN_PASSWORD_HASH")
    if explicit:
        return explicit
    plain = os.environ.get("ADMIN_PASSWORD")
    if plain:
        return generate_password_hash(plain)
    return _DEFAULT_HASH


def verify_admin(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False
    return check_password_hash(admin_password_hash(), password)


def login_user(username: str) -> None:
    session.clear()
    session["user"] = username
    session.permanent = True


def logout_user() -> None:
    session.clear()


def current_user() -> str | None:
    return session.get("user")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped
