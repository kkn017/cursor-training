# TODO: Demo Monitoring Infrastructure (Linux Servers)

Work in very small increments. Local demo only. Bind: **`0.0.0.0:5017`**.

Each step includes **security** and **documentation**.

---

## 1. Project initialization and basic UI

- [x] Create minimal layout: `app/`, `templates/`, `static/`, `tests/`
- [x] Add `requirements.txt` (Flask, pytest; pin versions)
- [x] Add `.gitignore` (venv, `__pycache__`, `.env`, local data files)
- [x] Scaffold Flask app with a simple home page
- [x] Bind app to `0.0.0.0` port `5017`
- [x] Add basic attractive UI shell (layout + CSS)
- [x] **Security:** No secrets in git; add `.env.example` only; note `0.0.0.0` is network-visible on local LAN
- [x] **Docs:** Minimal `README.md` — venv, install, run, open `http://localhost:5017`

---

## 2. Sign-in and unit tests

- [x] Add `/login` and `/logout` with Flask sessions
- [x] Default user `admin` with **hashed** password
- [x] Protect app routes (redirect to login if not signed in)
- [x] Simple login form UI
- [x] **Security:** Hashed passwords only; `SECRET_KEY` from env; HttpOnly session cookie
- [x] **Docs:** Document `admin` login and env vars for local demo
- [x] Unit tests: login OK / fail, protected redirect, logout, hash verify
- [x] Run tests with `pytest`

---

## 3. CI/CD (GitHub Actions)

- [x] Add `.github/workflows/ci.yml`
- [x] On push/PR: install deps + run `pytest`
- [x] Keep workflow minimal (optional light lint only)
- [x] **Security:** Do not echo secrets in CI logs
- [x] **Docs:** One short README note on what CI runs

---

## 4. Local server registry

- [x] Store servers locally (SQLite or JSON)
- [x] Fields: hostname/IP, SSH user, SSH port
- [x] Helpers: add, list, remove
- [x] **Security:** Validate host and port; keep credential-bearing files out of git
- [x] **Docs:** Where local server data is stored
- [x] Unit tests for add/list/remove + validation

---

## 5. Add / remove servers UI

- [x] Form: hostname/IP, SSH user, port
- [x] List servers; remove via POST
- [x] Require login for these actions
- [x] **Security:** CSRF protection (or equivalent); no delete via GET
- [x] **Docs:** How to add/remove a server in the UI
- [x] Tests: add/remove + auth required

---

## 6. SSH metrics collection

- [x] Add SSH library (e.g. Paramiko)
- [x] Collect: CPU %, memory used/free/%, network RX/TX, listening ports
- [x] Clear error when SSH/auth/collection fails
- [x] **Security:** Prefer SSH key; never log secrets; SSH timeouts; no unsafe remote command building from user input
- [x] **Docs:** Minimal local SSH setup for demo hosts
- [x] Unit tests with mocked SSH (success + failure)

---

## 7. Dashboard overview

- [x] Overview of all servers (reachable, CPU %, memory %)
- [x] Link to per-server detail
- [x] Show unreachable/error state
- [x] **Security:** Read-only metrics; login required
- [x] **Docs:** Brief overview description in README
- [x] Tests: auth + mocked overview render

---

## 8. Server drill-down and 5s refresh

- [x] Detail page: CPU, memory, network, ports
- [x] Auto-refresh every **5 seconds**
- [x] Show collection errors on the page
- [x] **Security:** Do not expose SSH credentials in HTML/JS/responses
- [x] **Docs:** Note refresh interval and how to open detail view
- [x] Tests: detail auth + mocked metrics

---

## 9. Demo polish

- [x] Empty/loading/error UI consistency
- [x] Check acceptance criteria in `docs/requirements.md`
- [x] **Security:** Final pass — hashed password, protected routes, no secrets in repo, input validation
- [x] **Docs:** Final README — local run on `0.0.0.0:5017`, login, add server, view metrics
- [x] Confirm CI is green

---

## Order

`1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9`
