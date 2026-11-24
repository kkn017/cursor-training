# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app for internal L1/L2/L3 and application teams to view real-time Linux server metrics without logging into each host.

**Problem:** Operators must SSH into servers to check CPU, memory, network, and port usage.

**Goal:** A read-only monitoring UI with admin sign-in and the ability to register Linux servers for SSH-based metric collection.

**Deployment:** Run locally on the machine where Cursor is running. Demo scope only.

**Bind address / port:** Listen on `0.0.0.0:5017` (all interfaces, port **5017**).

---

## 2. Users

| User | Access |
|------|--------|
| Internal L1 / L2 / L3 | View dashboards and server metrics (read-only) |
| Internal app / infra teams | Same |
| Admin (`admin`) | Sign in, add/remove servers, view metrics |

Single shared account for the demo: default username `admin` with a hashed password. No roles or multi-user management.

---

## 3. Goals & Non-Goals

### Goals

- Sign in with `admin` and hashed password
- Add Linux servers (hostname/IP, SSH user, SSH port)
- Collect metrics over SSH
- Show dashboard of all servers, then drill-down per server
- Auto-refresh metrics every **5 seconds**
- Attractive, simple Flask UI; metrics views are read-only

### Non-Goals (out of scope)

- Alerts / notifications
- Historical graphs or long-term storage
- Windows or non-Linux hosts
- Mobile app
- HTTPS / SSO
- Multi-user accounts or RBAC
- Docker / external database (keep local and minimal)

---

## 4. Features

### F1 — Read-only monitoring UI

- Clean, user-friendly UI for browsing metrics
- Metric views have no edit/delete of live data
- Admin may still add/remove servers and sign out

### F2 — Admin sign-in

- Default username: `admin`
- Password stored as a hash (not plain text)
- Session required to use the app
- Logout available
- Demo: one user is enough; no password-change UI required unless trivial to add

### F3 — Add Linux servers

- Form fields: **hostname/IP**, **SSH user**, **SSH port**
- Persist server list locally (e.g. SQLite or JSON file)
- Ability to remove a registered server
- SSH credentials for the demo: use a locally configured SSH key or password stored for demo use only (document in README when implementing)

### F4 — Real-time metrics (SSH)

For each server, collect via SSH:

| Metric | Details |
|--------|---------|
| CPU | Usage % |
| Memory | Used / free / % |
| Network | RX / TX |
| Ports | Listening / open port details |

- Refresh interval: **5 seconds**
- Show connection/error state if SSH or collection fails

### F5 — Dashboard + drill-down

1. **Overview:** list/cards of all registered servers with high-level status (e.g. reachable, CPU %, memory %)
2. **Detail:** per-server page with full CPU, memory, network, and port data

---

## 5. Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python |
| Web | Flask |
| UI | Attractive HTML/CSS (templates + simple JS for 5s refresh) |
| Data | Local file or SQLite |
| Collection | SSH to remote Linux hosts |
| Host | Local machine (Cursor environment) |

---

## 6. Local Run (minimal)

1. Create/activate a Python venv and install dependencies (`flask`, SSH client library, password hashing).
2. Set or seed default `admin` user with hashed password.
3. Ensure SSH access from this machine to target Linux hosts.
4. Start Flask app bound to `0.0.0.0` on port `5017` (e.g. `app.run(host="0.0.0.0", port=5017)`).
5. Open `http://localhost:5017` (or the host IP on port 5017), sign in as `admin`, add servers, view dashboard.

Exact package list and remaining commands belong in a short README at implementation time—not expanded here.

---

## 7. Acceptance Criteria

- [x] Unauthenticated users cannot see metrics
- [x] Can sign in as `admin` with hashed password verification
- [x] Can add a Linux server with hostname/IP, SSH user, and port
- [x] Can remove a server
- [x] Overview shows all registered servers
- [x] Drill-down shows CPU, memory, network, and ports for one server
- [x] Metrics refresh about every 5 seconds while the page is open
- [x] Failed SSH/collection shows a clear error/status
- [x] App runs locally with Flask without Docker or external DB
- [x] App binds to `0.0.0.0` on port `5017`

---

## 8. Open Items (implementer discretion)

- SSH auth method for demo (key vs password) — pick the simplest that works locally
- Exact commands used on remote hosts to gather metrics
- Visual design details (colors, charts vs plain numbers)
