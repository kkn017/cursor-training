"""Run the monitoring app locally on localhost:5017."""

from pathlib import Path


def _load_dotenv() -> None:
    """Load simple KEY=VALUE pairs from .env if present (no extra dependency)."""
    import os

    path = Path(__file__).resolve().parent / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


_load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5017, debug=True)
