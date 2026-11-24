# Server Monitor (Demo)

Local Flask demo for viewing Linux server metrics over SSH. Demo scope only — runs on the machine where you start it.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open **http://localhost:5017**

The app binds to `0.0.0.0:5017` (all interfaces). That means it is reachable on your local LAN, not only from this machine — use only on trusted networks.

## Environment

Copy `.env.example` to `.env` when you need local secrets (e.g. `SECRET_KEY` for sessions in a later step). Do not commit `.env`.

## Layout

| Path | Role |
|------|------|
| `app/` | Flask application package |
| `templates/` | Jinja HTML |
| `static/` | CSS / assets |
| `tests/` | pytest suite |
| `run.py` | Local entrypoint (`0.0.0.0:5017`) |
