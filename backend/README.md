# Backend

The backend is a single FastAPI application. GraphQL is the application data API at
`/graphql`; the only HTTP routes outside GraphQL are operational health checks.

## Local setup (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `APP_SECRET_KEY` in `.env` to a random value of at least 32 characters. To create the
first administrator, set all three `APP_BOOTSTRAP_ADMIN_*` values. The configured
administrator is created only when the database has no users; bootstrap settings do not
change an existing account.

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

The default SQLite database is stored under `backend/storage`. `APP_DATABASE_URL` can
override it with a SQLAlchemy URL. Schema changes are managed with Alembic; the
application does not create tables automatically.

## Initial implementation

- Environment-backed settings, structured logging, SQLite/PostgreSQL-compatible SQLAlchemy
  setup, and Alembic migrations.
- Argon2id password hashing, short-lived JWT access tokens, rotating opaque refresh tokens,
  revocation, and temporary lockout after repeated failed logins.
- GraphQL `me`, `login`, `refreshSession`, and `logout` operations.
- `/health/live` and `/health/ready` operational checks.
- Tests covering authentication and refresh-token rotation.

File-integrity monitoring, OS-specific log ingestion, detection, alerts, auditing,
subscriptions, and additional user-management operations are not implemented yet. They
will be added as backend phases with their own services, persistence, GraphQL operations,
and tests; no placeholder resolvers are exposed.

## Tests

```powershell
pytest
```
