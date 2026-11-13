# 🛡️ Data Integrity & Security Monitoring Platform

> A production-oriented security monitoring application that watches critical files, analyzes system security logs, detects suspicious activity, and raises actionable alerts — built as a single deployable Python backend with an Angular frontend, communicating over **GraphQL**.

---

## ✨ Overview

The platform combines two integrated security capabilities:

| Capability | Description |
|---|---|
| 📂 **Automated File Integrity Monitor (FIM)** | Establishes trusted **SHA-256 baselines** for approved directories and detects files that are created, modified, deleted, or moved |
| 🚨 **Smart Log Watcher & Threat Alerter** | Reads OS security log sources, parses security-relevant events, detects suspicious patterns (e.g. repeated authentication failures, privilege escalation) and raises alerts |

Monitoring runs **independently of the browser** — all events, baselines, alerts and audit records are persisted in the database, and the UI never shows hardcoded or fabricated statistics.

---

## 🧰 Tech Stack

### ⚙️ Backend
- 🐍 **Python 3.12+** with **FastAPI**
- 🍓 **Strawberry GraphQL** — queries, mutations & subscriptions (no REST business endpoints)
- 🗄️ **SQLAlchemy 2.x** + **Alembic** migrations (SQLite out of the box, PostgreSQL-ready)
- 🔒 **Argon2id** password hashing, **JWT** access tokens, rotating refresh tokens, account lockout
- 📡 GraphQL subscriptions over **WebSockets** for real-time updates
- 📅 **APScheduler** for periodic jobs
- 🪟 **watchdog** for filesystem events, Windows Event Log / journald adapters
- ✉️ **SMTP** email notifications

### 🎨 Frontend
- 🅰️ **Angular 17** + TypeScript
- 🚀 **Apollo Angular** GraphQL client
- 📈 **Chart.js** via ng2-charts for dashboards
- 🎨 SCSS styling

### 📡 Communication
- GraphQL endpoint: **`/graphql`** (HTTP for queries/mutations, WebSocket for subscriptions)
- Operational checks only: **`/health/live`** and **`/health/ready`**

---

## 📁 Project Structure

```text
📦 DataIntegritysecurityMonitoringPlatform
├── 📂 backend/            # 🐍 Single FastAPI application (modular, not microservices)
│   ├── app/
│   │   ├── modules/       # 🧩 auth · integrity · security_audit
│   │   ├── core/          # 🔒 security, settings
│   │   ├── database/      # 🗄️ SQLAlchemy setup
│   │   └── integrations/  # ✉️ email provider
│   ├── migrations/        # 🔄 Alembic
│   └── tests/             # 🧪 pytest suite
├── 📂 frontend/           # 🅰️ Angular dashboard (dashboard, alerts, audit,
│                          #    file integrity, log monitoring, reports,
│                          #    threat detection, user management)
├── 📄 PROJECT_REQUIREMENTS.md
└── 📄 Backend architecture.md
```

---

## 🚀 Getting Started

### ⚙️ Backend setup (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then open `.env` and:
- 🔑 Set `APP_SECRET_KEY` to a random value of **at least 32 characters**
- 👤 Set all three `APP_BOOTSTRAP_ADMIN_*` values to create the first administrator (created only when the database has no users)

Run migrations and start the server:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

🗄️ The default SQLite database lives under `backend/storage` (`APP_DATABASE_URL` can override it). Schema changes are managed with **Alembic**.

### 🎨 Frontend setup

```powershell
cd frontend
npm install
ng serve
```

> ⚠️ If you get *"The term 'ng' is not recognized"* — the Angular CLI isn't installed globally. Fix it with:
>
> ```powershell
> npm install -g @angular/cli@17
> ```
>
> (Alternatively, `npx ng serve` uses the project-local CLI without a global install.)

➡️ Open **http://localhost:4200** — the app talks to the backend GraphQL API at `http://localhost:8000/graphql`.

### 🔐 Admin bootstrap

The configured administrator is created **only if the database has no users**; bootstrap settings never overwrite an existing account.

---

## 🧪 Testing

```powershell
# 🐍 Backend
cd backend
pytest
```

Backend tests cover authentication flows and refresh-token rotation.

---

## 🚧 Implementation Status

| Area | Status |
|---|---|
| 🔐 Authentication (Argon2id, JWT, refresh rotation, lockout) | ✅ Done |
| 🗄️ SQLAlchemy + Alembic persistence, environment-backed settings, structured logging | ✅ Done |
| 💚 Health checks (`/health/live`, `/health/ready`) | ✅ Done |
| 🅰️ Angular dashboard UI (8 page modules) | ✅ Done |
| 📂 File integrity monitoring engine | 🚧 Planned phase |
| 📜 OS log ingestion (Windows Event Log / journald) | 🚧 Planned phase |
| 🚨 Threat detection & alerting | 🚧 Planned phase |
| 📡 GraphQL subscriptions | 🚧 Planned phase |
| ✉️ SMTP email notifications (config present) | 🚧 Planned phase |

> ℹ️ No placeholder resolvers are exposed — upcoming phases ship with their own services, persistence, GraphQL operations and tests.

---

## 📜 Core Principles

- 🧱 One deployable Python application — **no microservices**
- 🧩 Clearly separated modules; business logic lives in backend services, not resolvers
- 🔒 Secure defaults — no destructive actions without explicit authorization
- 🪟🐧 Windows & Linux supported through separate OS adapters
- 📊 Real data only — no hardcoded statistics on production dashboards

---

## 🤝 Contributing

1. Fork & clone the repo 🍴
2. Create a feature branch (`git checkout -b feature/amazing-feature`) 🌿
3. Commit your changes (`git commit -m "Add amazing feature"`) 💬
4. Push (`git push origin feature/amazing-feature`) ⬆️
5. Open a Pull Request 🎉

---

Built with ❤️ by **Rasul** · ⭐ Star the repo if you find it useful!
