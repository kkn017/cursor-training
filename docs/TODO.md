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

- [ ] Add `/login` and `/logout` with Flask sessions
- [ ] Default user `admin` with **hashed** password
- [ ] Protect app routes (redirect to login if not signed in)
- [ ] Simple login form UI
- [ ] **Security:** Hashed passwords only; `SECRET_KEY` from env; HttpOnly session cookie
- [ ] **Docs:** Document `admin` login and env vars for local demo
- [ ] Unit tests: login OK / fail, protected redirect, logout, hash verify
- [ ] Run tests with `pytest`

---

## 3. CI/CD (GitHub Actions)

- [ ] Add `.github/workflows/ci.yml`
- [ ] On push/PR: install deps + run `pytest`
- [ ] Keep workflow minimal (optional light lint only)
- [ ] **Security:** Do not echo secrets in CI logs
- [ ] **Docs:** One short README note on what CI runs

---

## 4. Local server registry

- [ ] Store servers locally (SQLite or JSON)
- [ ] Fields: hostname/IP, SSH user, SSH port
- [ ] Helpers: add, list, remove
- [ ] **Security:** Validate host and port; keep credential-bearing files out of git
- [ ] **Docs:** Where local server data is stored
- [ ] Unit tests for add/list/remove + validation

---

## 5. Add / remove servers UI

- [ ] Form: hostname/IP, SSH user, port
- [ ] List servers; remove via POST
- [ ] Require login for these actions
- [ ] **Security:** CSRF protection (or equivalent); no delete via GET
- [ ] **Docs:** How to add/remove a server in the UI
- [ ] Tests: add/remove + auth required

---

## 6. SSH metrics collection

- [ ] Add SSH library (e.g. Paramiko)
- [ ] Collect: CPU %, memory used/free/%, network RX/TX, listening ports
- [ ] Clear error when SSH/auth/collection fails
- [ ] **Security:** Prefer SSH key; never log secrets; SSH timeouts; no unsafe remote command building from user input
- [ ] **Docs:** Minimal local SSH setup for demo hosts
- [ ] Unit tests with mocked SSH (success + failure)

---

## 7. Dashboard overview

- [ ] Overview of all servers (reachable, CPU %, memory %)
- [ ] Link to per-server detail
- [ ] Show unreachable/error state
- [ ] **Security:** Read-only metrics; login required
- [ ] **Docs:** Brief overview description in README
- [ ] Tests: auth + mocked overview render

---

## 8. Server drill-down and 5s refresh

- [ ] Detail page: CPU, memory, network, ports
- [ ] Auto-refresh every **5 seconds**
- [ ] Show collection errors on the page
- [ ] **Security:** Do not expose SSH credentials in HTML/JS/responses
- [ ] **Docs:** Note refresh interval and how to open detail view
- [ ] Tests: detail auth + mocked metrics

---

## 9. Demo polish

- [ ] Empty/loading/error UI consistency
- [ ] Check acceptance criteria in `docs/requirements.md`
- [ ] **Security:** Final pass — hashed password, protected routes, no secrets in repo, input validation
- [ ] **Docs:** Final README — local run on `0.0.0.0:5017`, login, add server, view metrics
- [ ] Confirm CI is green

---

## Order

`1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9`
