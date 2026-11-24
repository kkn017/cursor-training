"""Demo monitoring application factory."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import current_user, login_required, login_user, logout_user, verify_admin
from app.csrf import ensure_csrf_token, validate_csrf_token
from app.metrics import collect_metrics_safe
from app.registry import RegistryError, ServerRegistry

SERVER_ID_RE = re.compile(r"^[0-9a-f]{32}$")
logger = logging.getLogger(__name__)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
        REGISTRY_PATH=str(
            Path(__file__).resolve().parent.parent / "data" / "servers.json"
        ),
    )
    if test_config:
        app.config.update(test_config)

    if (
        not app.config.get("TESTING")
        and app.config["SECRET_KEY"] in {"dev-only-change-me", "change-me-to-a-random-string"}
    ):
        logger.warning(
            "SECRET_KEY is using a default value. Set a strong SECRET_KEY in .env for local demos."
        )

    def registry() -> ServerRegistry:
        return ServerRegistry(Path(app.config["REGISTRY_PATH"]))

    def require_server_id(server_id: str) -> str:
        if not SERVER_ID_RE.match(server_id):
            abort(404)
        return server_id

    @app.context_processor
    def inject_globals():
        return {
            "current_user": current_user(),
            "csrf_token": ensure_csrf_token(),
        }

    @app.before_request
    def require_login():
        if request.endpoint in {None, "login", "static"}:
            return None
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return None

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user():
            return redirect(url_for("dashboard"))
        error = None
        username = ""
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            if verify_admin(username, password):
                login_user(username)
                ensure_csrf_token()
                nxt = request.args.get("next") or url_for("dashboard")
                if not nxt.startswith("/"):
                    nxt = url_for("dashboard")
                return redirect(nxt)
            error = "Invalid username or password."
        return render_template("login.html", error=error, username=username)

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        if not validate_csrf_token(request.form.get("csrf_token")):
            abort(400)
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def home():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        servers = registry().list_servers()
        rows = []
        for server in servers:
            metrics = collect_metrics_safe(
                server["hostname"], server["ssh_user"], int(server["ssh_port"])
            )
            rows.append({**server, "metrics": metrics})
        return render_template("dashboard.html", servers=rows)

    @app.route("/servers", methods=["GET", "POST"])
    @login_required
    def servers():
        reg = registry()
        error = None
        form = {"hostname": "", "ssh_user": "", "ssh_port": "22"}
        if request.method == "POST":
            if not validate_csrf_token(request.form.get("csrf_token")):
                abort(400)
            form = {
                "hostname": (request.form.get("hostname") or "").strip(),
                "ssh_user": (request.form.get("ssh_user") or "").strip(),
                "ssh_port": (request.form.get("ssh_port") or "22").strip(),
            }
            try:
                reg.add(form["hostname"], form["ssh_user"], form["ssh_port"])
                flash("Server added.", "ok")
                return redirect(url_for("servers"))
            except RegistryError as exc:
                error = str(exc)
        return render_template(
            "servers.html",
            servers=reg.list_servers(),
            error=error,
            form=form,
        )

    @app.route("/servers/<server_id>/remove", methods=["POST"])
    @login_required
    def remove_server(server_id: str):
        require_server_id(server_id)
        if not validate_csrf_token(request.form.get("csrf_token")):
            abort(400)
        if registry().remove(server_id):
            flash("Server removed.", "ok")
        else:
            flash("Server not found.", "error")
        return redirect(url_for("servers"))

    @app.route("/servers/<server_id>")
    @login_required
    def server_detail(server_id: str):
        require_server_id(server_id)
        server = registry().get(server_id)
        if not server:
            abort(404)
        metrics = collect_metrics_safe(
            server["hostname"], server["ssh_user"], int(server["ssh_port"])
        )
        return render_template(
            "server_detail.html",
            server=server,
            metrics=metrics,
            refresh_seconds=5,
        )

    return app
