# Server Monitor (Demo)

Local Flask demo for L1–L3 and app teams to view Linux server metrics over SSH—without logging into each host. Demo scope only.

**Bind:** `0.0.0.0:5017` (all interfaces — reachable on the local LAN; use only on trusted networks).

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # set a real SECRET_KEY
python run.py
```

Open **http://localhost:5017** (or `http://<host-ip>:5017` on the LAN).

## Demo walkthrough

1. **Sign in** with `admin` / `admin` (password is stored hashed; override via `ADMIN_PASSWORD` or `ADMIN_PASSWORD_HASH` in `.env`).
2. Open **Servers** → enter hostname/IP, SSH user, and port → **Add server**.
3. Open **Dashboard** for reachability, CPU %, and memory % across hosts.
4. Click **Details** for CPU, memory, network RX/TX, and listening ports. The detail view refreshes about every **5 seconds**.

Server list is stored in `data/servers.json` (created at runtime, gitignored). Remove a host only via the **Remove** button (POST + CSRF)—never via GET.

## Metric collection

- **`localhost` / `127.0.0.1`:** metrics are read on this machine (no SSH). Useful for a quick demo.
- **Remote hosts:** Paramiko over SSH. Prefer key-based auth:

```bash
ssh -i ~/.ssh/id_ed25519 USER@HOST
# optional: export SSH_KEY_PATH=~/.ssh/id_ed25519
```

Optional `SSH_PASSWORD` is supported for demos only—never commit it. Collection errors (timeouts, auth failures) show clearly on the dashboard and detail pages.

## Security notes (demo)

- Hashed admin password; Flask session cookie is **HttpOnly**
- `SECRET_KEY` from environment (do not commit `.env`)
- Protected routes redirect anonymous users to `/login`
- Host/user/port validated before save; CSRF on mutating forms
- No SSH private keys or live secrets in the repo

## Tests and CI

```bash
pytest
```

GitHub Actions (`.github/workflows/ci.yml`) installs dependencies and runs `pytest` on every push and pull request. Secrets are not echoed in CI logs.

## Layout

| Path | Role |
|------|------|
| `app/` | Flask application |
| `templates/` | Jinja HTML |
| `static/` | CSS |
| `tests/` | pytest suite |
| `data/` | Local registry (runtime only) |
| `run.py` | Entrypoint → `0.0.0.0:5017` |
