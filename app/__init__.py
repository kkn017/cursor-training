"""Demo monitoring application factory."""

from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    @app.route("/")
    def home():
        from flask import render_template

        return render_template("index.html")

    return app
