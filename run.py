"""Run the monitoring app locally on 0.0.0.0:5017."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # 0.0.0.0 makes the app reachable on the local LAN, not only localhost.
    app.run(host="0.0.0.0", port=5017, debug=True)
