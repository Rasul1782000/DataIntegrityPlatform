# Backend Architecture - Data Integrity & Security Monitoring Platform

## Project Structure

```
DataIntegritysecurityMonitoringPlatform/
├── backend/
│   ├── alembic/                      # Database migrations
│   ├── app/
│   │   ├── main.py                   # FastAPI entry point, lifecycle, routing, GraphQL integration
│   │   ├── schema.py                 # Root Strawberry GraphQL schema (stitches module schemas)
│   │   ├── core/                     # Global infrastructure & settings
│   │   │   ├── config.py             # Pydantic settings
│   │   │   ├── database.py           # SQLAlchemy engine & session maker
│   │   │   ├── exceptions.py         # Custom application exceptions
│   │   │   ├── logging.py            # Structured logging setup
│   │   │   └── security.py           # JWT, hashing, security utilities
│   │   │
│   │   ├── modules/                  # Feature-based domain modules
│   │   │   ├── auth/                 # Authentication & User Management Domain
│   │   │   │   ├── models.py         # SQLAlchemy models (User, RefreshSession)
│   │   │   │   ├── repository.py     # User & Auth database queries
│   │   │   │   ├── service.py        # Auth business logic & bootstrap admin
│   │   │   │   └── graphql/          # GraphQL schema elements for Auth
│   │   │   │       ├── types.py
│   │   │   │       ├── queries.py
│   │   │   │       └── mutations.py
│   │   │   │
│   │   │   ├── integrity/            # Future module: File hashing & checksum checks
│   │   │   │   ├── models.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── service.py
│   │   │   │   └── graphql/
│   │   │   │       ├── types.py
│   │   │   │       ├── queries.py
│   │   │   │       └── mutations.py
│   │   │   │
│   │   │   └── security_audit/       # Future module: Threat logs & alerts
│   │   │       ├── models.py
│   │   │       ├── repository.py
│   │   │       ├── service.py
│   │   │       └── graphql/
│   │   │           ├── types.py
│   │   │           ├── queries.py
│   │   │           └── mutations.py
│   │   │
│   │   ├── integrations/           # External service clients
│   │   │   └── notifications/
│   │   │       └── email_provider.py     # Email notifications
│   │   │
│   │   ├── schema.py                 # Root Strawberry GraphQL schema (stitches module schemas)
│   │   └── main.py                   # FastAPI entry point, CORS, lifespan, /graphql
│   │
│   ├── storage/                      # Local storage / backup holding
│   ├── tests/                        # Test suite mirroring module structure
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   └── ...
└── PROJECT_REQUIREMENTS.md
```

## Key Architectural Pattern: Feature-First (Domain-Driven)

The backend follows a **feature-first architecture** where files are grouped by **business domain/capability** rather than technical layers. This eliminates the "jump around" problem where modifying a single feature requires editing files across 5-6 different directories.

### Module Structure

Each module is self-contained with:
- **models.py** - SQLAlchemy database models
- **repository.py** - Database query operations
- **service.py** - Business logic
- **graphql/types.py** - GraphQL type definitions
- **graphql/queries.py** - GraphQL query resolvers
- **graphql/mutations.py** - GraphQL mutation resolvers

### Core Infrastructure (app/core/)

Global infrastructure that supports all modules:
- **config.py** - Pydantic settings with environment variable loading
- **database.py** - SQLAlchemy engine and session factory creation
- **exceptions.py** - Custom exception classes (AuthenticationError, AuthorizationError)
- **security.py** - JWT operations, password hashing, token generation, password verification

### Module: auth (Authentication & User Management)

The core domain module containing:
- **models.py** - User and RefreshSession SQLAlchemy models
- **repository.py** - UserRepository and AuthRepository for database operations
- **service.py** - AuthService implementing login, refresh, logout, and bootstrap admin creation
- **graphql/types.py** - UserType and AuthPayload GraphQL types
- **graphql/queries.py** - AuthQueries with `me` field for current user
- **graphql/mutations.py** - AuthMutations with login, refresh_session, and logout fields

### Root Application (app/main.py)

Thin FastAPI application initializer that:
- Configures logging and settings
- Creates database engine and session factory
- Validates APP_SECRET_KEY minimum 32 characters
- Handles bootstrap admin credential setup
- Registers CORS middleware
- Mounts GraphQL router at `/graphql` prefix
- Provides health check endpoints (`/health/live`, `/health/ready`)

### Root GraphQL Schema (app/schema.py)

Strawberry GraphQL schema that imports and combines types/queries/mutations from all feature modules. Currently includes the auth module, with integrity and security_audit modules planned as extensions.

### Integrations (app/integrations/)

External service clients:
- **email_provider.py** - SMTP-based email notification provider configurable via environment variables

### Testing (tests/)

Test suite with conftest.py for creating test clients and fixture setup. Uses the new module import paths.

## Technology Stack

- **FastAPI** - Web framework API
- **SQLAlchemy 2.0** - ORM for database interactions (DeclarativeBase style)
- **Strawberry GraphQL** - GraphQL integration with FastAPI
- **Pydantic** - Settings and data validation (pydantic-settings for environment config)
- **Alembic** - Database migration tool
- **Python >= 3.12** - Runtime version

## Design Rationale

### Why Feature-First Architecture?

1. **High Cohesion, Low Coupling**: All code related to a business feature lives in one directory. Authentication code is entirely within `app/modules/auth/` - no need to jump between models/, repositories/, services/, and graphql/ directories.

2. **Scalable Organization**: When adding new features (file integrity monitoring, security audit logging, etc.), you simply create a new module folder inside `app/modules/` without disrupting existing code.

3. **Clean Root Application**: `main.py` remains focused on FastAPI initialization, middleware, and routing - not bloated with business logic.

4. **Unified GraphQL Schema Stitching**: The root `schema.py` simply imports and combines schema elements from each module, keeping the GraphQL layer modular and maintainable.

5. **Ready for Scale**: The platform can grow to handle file integrity monitors, log streaming pipelines, threat alert systems, and more by simply adding new modules without restructuring existing code.

### Comparison: Layered vs Feature-First

| Aspect | Traditional Layered | Feature-First (This Architecture) |
|--------|---------------------|-----------------------------------|
| **Auth modification** | Edit 5-6 files in 4 directories | Edit 1 directory: `app/modules/auth/` |
| **New feature addition** | Requires restructuring | Just add new module folder |
| **Root application** | Grows organically, becomes messy | Stays thin and focused |
| **GraphQL schema** | Fragmented across global directories | Stitched from module exports |
| **Scale readiness** | Requires refactoring when growing | Built to grow from the start |

## Current Modules

- **auth** - Authentication & User Management (fully implemented)
- **integrity** - File hashing & checksum checks (placeholder, ready for extension)
- **security_audit** - Threat logs & alerts (placeholder, ready for extension)

## Future Extensions

Add new modules inside `app/modules/` for:
- File integrity monitoring (FIM)
- Security information and event management (SIEM)
- File integrity alerting
- Audit log streaming
- And any other business capability