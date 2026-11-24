"""Simple session CSRF tokens (no third-party dependency)."""

from __future__ import annotations

import secrets

from flask import session


def ensure_csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_hex(32)
        session["_csrf_token"] = token
    return token


def validate_csrf_token(token: str | None) -> bool:
    expected = session.get("_csrf_token")
    if not expected or not token:
        return False
    return secrets.compare_digest(expected, token)
