# Data Integrity & Security Monitoring Platform
## Production-Ready Project Requirements and AI Coding-Agent Specification

**Project name:** Data Integrity & Security Monitoring Platform  
**Architecture:** Monolithic application  
**Frontend:** Angular (latest stable version available at project setup)  
**Backend:** Python 3.12+ with FastAPI  
**Application API:** GraphQL using Strawberry  
**Frontend GraphQL client:** Apollo Angular  
**Database:** SQLite for initial deployment, with SQLAlchemy abstractions that permit PostgreSQL migration  
**Real-time updates:** GraphQL Subscriptions over WebSockets  
**File monitoring:** `hashlib`, `pathlib`, `watchdog`  
**Log monitoring:** OS-specific adapters, `re`, Windows Event Log integration where available  
**Scheduling:** APScheduler or an equivalent in-process scheduler  
**Testing:** pytest, Angular testing tools

---

# 1. Project objective

Build a production-oriented security monitoring application that helps authorized administrators monitor critical files and directories, detect integrity changes, analyze supported operating-system security logs, identify suspicious activity, and investigate alerts.

The application consists of two integrated security capabilities:

1. **Automated File Integrity Monitor (FIM):** Establishes trusted SHA-256 baselines for approved directories and detects files created, modified, deleted, moved or otherwise changed.
2. **Smart Log Watcher & Threat Alerter:** Reads supported system log sources, parses security-relevant events, detects suspicious patterns such as repeated authentication failures and privilege escalation, and raises actionable alerts.

The result must be a working application, not only a dashboard mock-up. Angular must communicate with the Python backend through GraphQL for application data operations. Do not create REST business endpoints.

## 1.1 Core principles

- Use one deployable Python backend application: **do not use microservices**.
- Keep the frontend and backend in separate root-level folders.
- Organize both codebases into clearly separated modules.
- Keep business logic in backend services, not GraphQL resolvers.
- Run file and log monitoring independently of the browser and Angular session.
- Persist events, baselines, alerts and audit records in the database.
- Use secure defaults. Never perform destructive or disruptive response actions without explicit authorization.
- Support Windows and Linux through separate operating-system adapters. Do not assume their log formats or permissions are identical.
- Do not use hardcoded or fabricated statistics in production dashboard screens.

---

# 2. Technology stack

## 2.1 Frontend

- Angular, latest stable release available at implementation time
- TypeScript
- Angular Standalone Components
- Angular Router
- Angular Reactive Forms
- Angular Signals and RxJS where appropriate
- Apollo Angular
- GraphQL Code Generator for typed operations
- SCSS
- Angular CDK
- PrimeNG or Angular Material (choose one consistent component system)
- Apache ECharts or Chart.js for charts

## 2.2 Backend

- Python 3.12+
- FastAPI for application hosting and lifecycle management
- Strawberry GraphQL for schema, queries, mutations and subscriptions
- SQLAlchemy 2.x
- Alembic
- SQLite initially
- Pydantic for configuration and validation where appropriate
- `hashlib` for SHA-256
- `pathlib` for filesystem paths
- `watchdog` for filesystem events
- `re` for supported text-log parsing
- `ipaddress` for IP validation and normalization
- APScheduler for periodic jobs
- `psutil` for selected system information, if required
- `win32evtlog` / pywin32 for Windows Event Log integration
- Linux journald integration and supported text-log adapters
- `smtplib` or a maintained mail library for email notifications
- pytest for backend tests

## 2.3 Communication

**Use GraphQL as the application data API.**

- GraphQL endpoint: `/graphql`
- Queries: read application data
- Mutations: create, update, approve, acknowledge and resolve application records
- Subscriptions: stream authorized real-time events to connected clients
- Apollo Angular: execute frontend GraphQL operations
- WebSocket transport: GraphQL subscriptions
- HTTP transport: GraphQL queries and mutations

FastAPI may expose narrowly scoped operational endpoints only when required for infrastructure concerns such as health checks, readiness checks or metrics. Do not use REST endpoints for application business operations.

## 2.4 Database and storage

- SQLite for the initial single-host deployment.
- SQLAlchemy repositories for all database access.
- Alembic for schema migrations.
- Store the database, application logs, audit exports and reports in configurable storage locations.
- Design the repository and configuration layers so PostgreSQL can be introduced later without rewriting business logic.

---

# 3. Monolithic architecture

Build one Python application with modular internal boundaries. Modules must not be separately deployable services.

```text
data-integrity-security/
├── frontend/
├── backend/
├── storage/
├── scripts/
├── docs/
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 3.1 Backend architecture

```text
backend/
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   └── logging_config.py
│   ├── core/
│   │   ├── security.py
│   │   ├── permissions.py
│   │   ├── exceptions.py
│   │   └── lifecycle.py
│   ├── database/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── workers/
│   │   ├── scheduler.py
│   │   ├── fim_worker.py
│   │   ├── log_worker.py
│   │   └── event_publisher.py
│   ├── integrations/
│   │   ├── operating_system/
│   │   │   ├── base.py
│   │   │   ├── windows.py
│   │   │   └── linux.py
│   │   ├── firewall/
│   │   │   ├── base.py
│   │   │   ├── windows_firewall.py
│   │   │   └── linux_firewall.py
│   │   └── notifications/
│   │       └── email_provider.py
│   ├── modules/
│   │   ├── authentication/
│   │   ├── dashboard/
│   │   ├── file_integrity/
│   │   ├── log_monitoring/
│   │   ├── threat_detection/
│   │   ├── alerts/
│   │   ├── audit/
│   │   ├── reports/
│   │   └── settings/
│   └── graphql/
│       ├── __init__.py
│       ├── schema.py
│       ├── context.py
│       ├── scalars.py
│       ├── types/
│       ├── queries/
│       ├── mutations/
│       └── subscriptions/
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── requirements.txt
├── .env.example
└── pyproject.toml
```

Each backend module should contain its own service and repository logic where appropriate. GraphQL resolvers must call these services; they must not contain filesystem scanning, log reading, hashing, threat detection or firewall execution logic.

## 3.2 Frontend architecture

```text
frontend/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── apollo/
│   │   │   │   ├── apollo.config.ts
│   │   │   │   ├── auth-link.ts
│   │   │   │   └── error-link.ts
│   │   │   ├── authentication/
│   │   │   ├── guards/
│   │   │   └── interceptors/
│   │   ├── layouts/
│   │   │   ├── main-layout/
│   │   │   └── auth-layout/
│   │   ├── shared/
│   │   │   ├── components/
│   │   │   ├── directives/
│   │   │   ├── pipes/
│   │   │   └── models/
│   │   ├── modules/
│   │   │   ├── dashboard/
│   │   │   ├── file-integrity/
│   │   │   ├── log-monitoring/
│   │   │   ├── threat-detection/
│   │   │   ├── alerts/
│   │   │   ├── audit/
│   │   │   ├── reports/
│   │   │   ├── settings/
│   │   │   └── user-management/
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   ├── assets/
│   ├── environments/
│   └── styles/
├── codegen.ts
├── angular.json
├── package.json
└── tsconfig.json
```

Each feature module must have separate page components, reusable components, services, models and GraphQL operation files. Do not put all screens or logic in the root component.

Example feature structure:

```text
file-integrity/
├── pages/
│   ├── fim-dashboard/
│   ├── monitored-directories/
│   ├── file-change-history/
│   ├── integrity-baselines/
│   └── scan-details/
├── components/
│   ├── integrity-score-card/
│   ├── file-change-table/
│   ├── file-status-badge/
│   ├── scan-progress/
│   └── hash-comparison/
├── services/
│   └── file-integrity.service.ts
├── graphql/
│   ├── fim.queries.graphql
│   ├── fim.mutations.graphql
│   └── fim.subscriptions.graphql
└── models/
    └── file-integrity.model.ts
```

---

# 4. Application modules and navigation

The application must include the following navigation:

1. Overview Dashboard
2. File Integrity Monitoring
3. Monitored Directories
4. File Change History
5. Integrity Baselines
6. Scan History
7. Log Monitoring
8. Log Sources
9. Live Log Viewer
10. Authentication Events
11. Threat Detection
12. Detection Rules
13. Suspicious IP Addresses
14. Security Alerts
15. Audit Trail
16. Reports
17. Settings
18. User Management

Enforce role-based visibility and backend authorization. Hiding a menu item in Angular is not a substitute for backend permission checks.

---

# 5. Dashboard requirements

Create an enterprise security operations dashboard.

Display real data retrieved through GraphQL:

- Number of monitored directories
- Total files in approved baselines
- Files modified today
- Files added today
- Files deleted today
- Last successful integrity scan
- Total log events processed
- Failed authentication attempts
- Active threats
- Critical alerts
- Monitoring service health
- Log sources with errors or interruptions

Charts:

- File changes over time
- Created, modified and deleted file counts
- Authentication successes versus failures
- Security events by severity
- Threat detection timeline
- Most frequently observed source IPs

Dashboard cards and charts must use typed GraphQL query results. Use loading, empty, partial-data and error states. Do not invent sample values in production. Clearly label synthetic values in development fixtures.

---

# 6. Automated File Integrity Monitor (FIM)

## 6.1 Directory registration

Authorized administrators must be able to register a directory with:

- Display name
- Absolute directory path
- Description
- Recursive monitoring setting
- Enabled/paused state
- Scan interval
- Included file extensions (optional)
- Excluded file extensions (optional)
- Excluded subdirectories
- Maximum file size
- Monitoring priority

Validate that the path exists and is accessible. Canonicalize paths and enforce an administrator-approved monitoring-root policy. Prevent path traversal and unsafe symbolic-link traversal. Do not silently broaden a user's approved scope.

## 6.2 SHA-256 calculation

Use chunked reads so large files are not loaded entirely into memory.

```python
import hashlib
from pathlib import Path

def calculate_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()
```

Production implementation must also:

- Handle permission errors and files disappearing during a scan.
- Avoid following symlinks outside the approved root.
- Detect files changing while they are being hashed and retry or record an unstable-file result.
- Record scan errors without terminating the entire directory scan.
- Avoid hashing excluded files.
- Support cancellation and progress reporting for long scans.

## 6.3 Trusted baseline

When monitoring is first enabled, an authorized administrator can create a baseline.

Store:

- Directory ID
- Canonical file path relative to the monitored root
- SHA-256 hash
- File size
- Modification timestamp
- File metadata supported by the OS
- Baseline version
- Scan ID
- Creation timestamp
- User who approved the baseline

A baseline is a trusted reference, not an automatically updated snapshot. Never silently accept detected modifications into the trusted baseline.

Require an authorized user to review and approve baseline updates. Preserve baseline history.

## 6.4 Change detection

Compare each completed scan with the trusted baseline.

Supported event types:

| Event | Meaning |
|---|---|
| `CREATED` | File exists now but was not in the baseline |
| `MODIFIED` | Content hash differs from the baseline |
| `DELETED` | Baseline file is no longer present |
| `MOVED` | A file was moved to another path, when confidently identified |
| `PERMISSION_CHANGED` | Relevant file permissions changed |
| `SCAN_ERROR` | File could not be reliably inspected |

For every event, persist:

- Event ID
- Directory ID
- Relative file path
- Event type
- Previous hash
- Current hash
- File size where available
- Detection method
- Severity
- Detection timestamp
- Investigation status
- Related scan ID

Do not claim a rename or move solely because one file disappeared and another appeared. Only classify it as a move when identity can be established with a documented, reliable matching method; otherwise report deletion and creation.

## 6.5 Real-time and periodic monitoring

Use Watchdog handlers for:

- `on_created`
- `on_modified`
- `on_deleted`
- `on_moved`

Filesystem events are hints that trigger verification. They are not the source of truth. Events may be duplicated, coalesced or missed. Run periodic full reconciliation scans against the trusted baseline.

Prevent duplicate and overlapping scans for the same directory. Persist scan state and recover safely after process restart.

## 6.6 Scan scheduling

Allow administrators to select:

- Every 5 minutes
- Every 15 minutes
- Every 30 minutes
- Every hour
- Every 6 hours
- Every 12 hours
- Daily
- Manual only

Validate minimum intervals and resource limits. Use APScheduler or an equivalent scheduler. A long-running scan must not block GraphQL request handling.

## 6.7 FIM user actions

Authorized users can:

- Register and edit monitored directories
- Pause and resume monitoring
- Start a manual scan
- View scan progress and history
- Compare previous and current hashes
- Investigate file events
- Mark a change as authorized with a reason
- Mark a change as unauthorized
- Propose and approve a baseline update
- Export a scan report

---

# 7. Smart Log Watcher

## 7.1 Supported log sources

Implement operating-system-specific adapters.

**Linux sources may include:**

- `/var/log/auth.log`
- `/var/log/secure`
- `/var/log/syslog`
- systemd journal

**Windows sources may include:**

- Security Event Log
- System Event Log
- Application Event Log

Use `win32evtlog` or an appropriate Windows API for Windows Event Logs. Do not treat Windows Event Logs as ordinary text files.

Log access requires appropriate operating-system permissions. Explain required permissions during setup and fail safely when access is denied.

## 7.2 Log ingestion

Implement:

- Incremental reading
- Continuous monitoring
- Source identification
- Timestamp parsing and normalization to UTC
- Log rotation handling
- Truncation handling
- Duplicate event prevention
- Source disconnection/error detection
- Bounded buffering and backpressure
- Safe handling of malformed or oversized records

Use a stable cursor/offset strategy appropriate to each source. Do not rely only on line numbers, because log rotation and truncation can invalidate them.

Retain raw log content only when configured and necessary. Redact secrets and sensitive values from application logs and user-facing views.

## 7.3 Detection rules

Create configurable, testable detection rules.

| Rule | Example condition | Suggested severity |
|---|---|---|
| Repeated failed login | 5 failures from one source within 5 minutes | High |
| Brute-force pattern | 15 failures from one source within 10 minutes | Critical |
| Privilege escalation | A supported suspicious sudo/admin event | High |
| Failure followed by success | Successful login after repeated failures from the same source/account | High |
| Unusual admin activity | An enabled rule identifies unexpected admin activity | Medium–High |
| Multi-account targeting | Repeated failures against several accounts from one source | High |

Thresholds are configurable. These are starting examples, not universal indicators of compromise. Avoid treating a single event or IP address as proof of malicious activity.

Each rule must include:

- Rule ID and name
- Description
- Event category
- Source/platform applicability
- Detection logic or parser identifier
- Threshold and time window, where applicable
- Severity
- Enabled state
- Version
- Created/updated metadata

Use regular expressions only for supported text-log formats. Prefer structured fields for Windows events and journald. Validate patterns, bound input sizes and avoid unsafe or catastrophic regular-expression behavior.

## 7.4 IP address intelligence

Extract and validate addresses using Python's `ipaddress` module.

Store, where available:

- Normalized IP address
- First and last observed timestamps
- Failed and successful authentication counts
- Associated usernames
- Related event IDs
- Severity and investigation status

Do not label every address as malicious. Distinguish private, loopback, link-local and public addresses. Do not perform external reputation lookups unless explicitly configured and privacy-reviewed.

---

# 8. Threat response and firewall safety

The default response is to create an alert and recommend investigation.

Supported actions:

1. Generate an in-application alert.
2. Send an email alert.
3. Mark an address for investigation.
4. Recommend a firewall block.
5. Execute a temporary firewall block only after authorized approval.
6. Record the action and its result.

Firewall blocking must be disabled by default. Require explicit administrator approval and implement:

- OS-specific firewall adapters
- Strict IP/CIDR validation
- Trusted/allowlisted management addresses
- Protection against blocking loopback and essential management paths
- Temporary block expiry
- Authorization identity and timestamp
- Execution result and error record
- Emergency unblocking procedure
- Audit record for block and unblock actions

Never execute shell commands built from raw log content. Use safe APIs or carefully constructed argument arrays with validated inputs. Do not make automatic firewall changes based solely on a regular-expression match.

---

# 9. Alerts and notifications

Provide:

- In-application alerts
- Email notifications
- Optional outbound webhooks, disabled until configured

Email settings:

- SMTP host and port
- Sender and recipient
- Authentication method
- TLS configuration
- Secret reference

Do not return SMTP credentials to the frontend or store them in plaintext. Use environment variables or a secure secrets store.

Alert categories include:

- File created, modified or deleted
- Baseline mismatch
- Scan error
- Repeated login failures
- Brute-force pattern
- Privilege escalation event
- Suspicious authentication sequence
- Monitoring source unavailable
- Firewall action result

Alert lifecycle:

- New
- Acknowledged
- Investigating
- Resolved
- False positive

Support assignment, investigation notes, timestamps and a complete status history. Avoid sending duplicate notifications for every repeated event; implement configurable deduplication and cooldown rules.

---

# 10. Authentication and authorization

Implement secure authentication and role-based authorization.

Suggested roles:

- **Administrator:** Full configuration and user management permissions.
- **Security Analyst:** View events, investigate threats and manage alerts.
- **Auditor:** Read-only access to approved reports and audit records.
- **Viewer:** Read-only access to permitted dashboards.

Requirements:

- Argon2id password hashing
- Secure session/token lifecycle
- Short-lived access tokens and controlled refresh
- Secure token storage strategy
- Rate limiting for authentication
- Account lockout or throttling policy
- GraphQL field and operation authorization
- Authorization checks on every sensitive resolver and service action
- WebSocket subscription authentication and authorization
- Audit logging for security-sensitive actions

Do not rely on Angular route guards or hidden UI controls for security. Enforce permissions in the backend.

---

# 11. Database design

Use SQLAlchemy models, repository classes and Alembic migrations.

Core entities:

## Users

- id
- username
- email
- password_hash
- role
- is_active
- created_at
- updated_at

## MonitoredDirectories

- id
- name
- canonical_path
- description
- recursive
- monitoring_enabled
- scan_frequency
- created_by
- created_at
- updated_at

## ScanRuns

- id
- directory_id
- status
- started_at
- completed_at
- files_examined
- errors_count
- initiated_by
- error_summary

## FileBaselines

- id
- directory_id
- relative_path
- sha256_hash
- file_size
- modified_at
- baseline_version
- scan_id
- approved_by
- created_at

## FileIntegrityEvents

- id
- directory_id
- scan_id
- relative_path
- event_type
- previous_hash
- current_hash
- severity
- status
- detected_at

## LogSources

- id
- source_name
- source_type
- source_path
- operating_system
- monitoring_enabled
- last_read_at
- health_status
- created_at

## SecurityEvents

- id
- source_id
- source_event_id
- event_category
- username
- source_ip
- normalized_timestamp
- event_description
- raw_event_reference
- severity
- created_at

## DetectionRules

- id
- rule_name
- description
- rule_type
- threshold
- time_window_seconds
- severity
- enabled
- version
- created_at
- updated_at

## Threats

- id
- threat_type
- severity
- status
- source_ip
- first_seen_at
- last_seen_at
- created_at

## ThreatEvents

- threat_id
- security_event_id

## Alerts

- id
- alert_type
- title
- description
- severity
- status
- assigned_to
- deduplication_key
- created_at
- resolved_at

## AlertHistory

- id
- alert_id
- actor_id
- action
- note
- created_at

## FirewallActions

- id
- ip_address
- action_type
- authorization_status
- authorized_by
- expires_at
- execution_status
- result_summary
- created_at

## AuditLogs

- id
- actor_id
- action
- entity_type
- entity_id
- previous_value
- new_value
- timestamp
- previous_record_hash
- record_hash

Use foreign keys, uniqueness constraints and indexes for timestamps, severity, event categories, file paths, source IPs and lookup fields. Use migrations rather than relying on automatic table creation in production.

---

# 12. GraphQL API specification

## 12.1 Communication rules

- GraphQL is the application data API.
- Use one GraphQL schema composed from modular types and resolver modules.
- Use GraphQL Queries for reads.
- Use GraphQL Mutations for writes and actions.
- Use GraphQL Subscriptions for real-time event delivery.
- Use Apollo Angular in the frontend.
- Use GraphQL Code Generator to generate TypeScript types and operation definitions.
- Do not create REST business endpoints.
- Keep resolvers thin; call service and repository layers.
- Apply authentication, authorization, input validation and audit requirements to every sensitive operation.
- Implement pagination, filtering and sorting consistently.
- Apply query depth and complexity limits, request-size limits and rate limits.
- Avoid N+1 database queries; use eager loading or Strawberry DataLoaders where needed.
- Never expose raw exception traces or secrets through GraphQL errors.

## 12.2 GraphQL schema organization

```text
graphql/
├── schema.py
├── context.py
├── scalars.py
├── types/
│   ├── common_types.py
│   ├── user_type.py
│   ├── dashboard_type.py
│   ├── file_integrity_type.py
│   ├── scan_type.py
│   ├── log_event_type.py
│   ├── threat_type.py
│   ├── alert_type.py
│   └── audit_type.py
├── queries/
│   ├── auth_queries.py
│   ├── dashboard_queries.py
│   ├── fim_queries.py
│   ├── log_queries.py
│   ├── threat_queries.py
│   ├── alert_queries.py
│   └── audit_queries.py
├── mutations/
│   ├── auth_mutations.py
│   ├── fim_mutations.py
│   ├── log_mutations.py
│   ├── threat_mutations.py
│   ├── alert_mutations.py
│   └── settings_mutations.py
└── subscriptions/
    ├── fim_subscriptions.py
    ├── log_subscriptions.py
    └── alert_subscriptions.py
```

## 12.3 Required query capabilities

Implement GraphQL queries for:

- Current authenticated user
- Dashboard summary and chart series
- Monitored directories and directory details
- File integrity events and event details
- Baselines and baseline history
- Scan runs and scan progress
- Log sources and source health
- Security events and event details
- Threats and threat details
- Detection rules
- Suspicious IP summaries
- Alerts and alert history
- Audit records
- Reports and settings

## 12.4 Required mutations

Implement GraphQL mutations for:

- Login, logout and token refresh according to the chosen auth model
- Register, update, pause and resume a monitored directory
- Start and cancel a scan
- Approve a baseline update
- Mark a file event authorized or unauthorized
- Register, update, enable and disable a log source
- Create, update and enable/disable detection rules
- Acknowledge, assign and resolve an alert
- Add investigation notes
- Request an approved firewall action
- Approve or reject a firewall action
- Configure notification settings
- Manage users and roles, subject to permissions

Long-running actions such as scans should return a job/scan identifier and status. Do not keep a GraphQL request open until a large scan completes.

## 12.5 Required subscriptions

Implement authenticated and authorized subscriptions for:

- `fileIntegrityEvent`
- `scanProgress`
- `securityLogEvent`
- `threatDetected`
- `securityAlert`
- `monitoringHealthChanged`

Subscriptions should publish persisted events, not uncommitted in-memory-only state. Define bounded queues, backpressure, disconnect handling and reconnect behavior. Re-query authoritative state after reconnect because a WebSocket may disconnect and miss events.

## 12.6 Example GraphQL operations

Dashboard query:

```graphql
query GetDashboardSummary {
  dashboardSummary {
    totalMonitoredDirectories
    totalMonitoredFiles
    modifiedFilesToday
    addedFilesToday
    deletedFilesToday
    totalLogEvents
    failedLoginAttempts
    activeThreats
    criticalAlerts
    lastSuccessfulScan
  }
}
```

Directory registration mutation:

```graphql
mutation RegisterDirectory($input: DirectoryInput!) {
  registerDirectory(input: $input) {
    directory {
      id
      name
      canonicalPath
      monitoringEnabled
    }
    errors {
      code
      message
      field
    }
  }
}
```

Start scan mutation:

```graphql
mutation StartIntegrityScan($directoryId: ID!) {
  startIntegrityScan(directoryId: $directoryId) {
    scan {
      id
      status
      startedAt
    }
    errors {
      code
      message
    }
  }
}
```

File event subscription:

```graphql
subscription FileIntegrityEvents($directoryId: ID) {
  fileIntegrityEvent(directoryId: $directoryId) {
    id
    relativePath
    eventType
    previousHash
    currentHash
    severity
    detectedAt
  }
}
```

Security alert subscription:

```graphql
subscription SecurityAlerts {
  securityAlert {
    id
    title
    description
    severity
    status
    createdAt
  }
}
```

Use generated operation types in Angular. Adapt exact GraphQL names and scalar representations consistently in the implemented schema.

## 12.7 FastAPI and Strawberry integration

Mount Strawberry's GraphQL router at `/graphql`. Configure request context to provide the authenticated principal, database session or session factory, authorization services, DataLoaders and event broker.

Use FastAPI lifecycle hooks to initialize and stop application resources. Do not create a new unbounded database session or background scheduler per request.

Example integration shape (complete imports and context implementation are required in the real project):

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.graphql.context import get_context

app = FastAPI(title="Data Integrity & Security Monitoring Platform")

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_router, prefix="/graphql")
```

Operational health/readiness routes may be added separately if needed; application business data must remain on GraphQL.

---

# 13. Angular and Apollo Angular requirements

Configure Apollo Angular with:

- GraphQL HTTP link targeting the configured backend `/graphql` URL
- WebSocket link for subscriptions
- Correct split-link routing for subscriptions versus queries/mutations
- Authentication link
- Centralized GraphQL error handling
- Typed generated operations
- Cache policies appropriate to changing security data
- Subscription cleanup when components are destroyed
- Reconnection handling
- Loading, empty, partial and error states

Store authentication credentials using a secure strategy. Do not put long-lived secrets in local storage. Configure cookies, CSRF protections and token transport consistently with the selected authentication design.

Each feature must use its own GraphQL operation files and feature service. Components should not construct large GraphQL documents inline.

---

# 14. User interface and visual design

Build a professional, modern enterprise security dashboard inspired by security operations center and endpoint monitoring products.

## 14.1 Visual theme

Use a clean light theme:

- Primary blue: `#2563EB`
- Dark navy: `#0F172A`
- Page background: `#F8FAFC`
- Card background: `#FFFFFF`
- Border: `#E2E8F0`
- Primary text: `#111827`
- Secondary text: `#64748B`
- Healthy: green
- Warning: yellow
- High risk: orange
- Critical: red
- Informational: blue

Use color alongside text and icons; do not communicate severity by color alone.

## 14.2 Layout

**Sidebar:** Logo, Overview, File Integrity, Log Monitoring, Threat Detection, Alerts, Audit Trail, Reports, Settings.

**Header:** Page title, breadcrumb, global search, notification indicator, monitoring health, profile menu.

**Main content:** Clear page hierarchy, whitespace, consistent cards, readable tables and contextual actions.

## 14.3 Required detailed screens

**File change details:**

- Relative file path and monitored directory
- Previous and current SHA-256
- Detection timestamp
- File size and relevant metadata
- Event classification
- Baseline version
- Investigation history
- Authorization and baseline update actions, subject to permissions

**Threat details:**

- Threat category and severity
- Source IP and username where available
- Related events and timeline
- First and last observed
- Triggered detection rule
- Investigation status and notes
- Recommended response
- Firewall action status, if applicable

**Live log viewer:**

- Source selector
- Time range
- Severity and category filters
- Search
- Pause/resume visual stream
- Event details drawer
- Clear indication when the stream is disconnected or delayed

All tables should support server-side pagination, sorting and filtering through GraphQL.

Ensure responsive desktop, tablet and mobile layouts. Do not overload the overview screen with every metric.

---

# 15. Audit trail and application security

## 15.1 Audit records

Record security-sensitive actions, including:

- Authentication success/failure
- User and role changes
- Directory registration and configuration changes
- Baseline creation and approval
- File event decisions
- Detection rule changes
- Alert status changes
- Firewall action requests, approvals and results
- Notification configuration changes

Use hash chaining with previous-record hashes and record hashes to make tampering detectable. Protect audit storage and signing keys separately where feasible. A hash chain stored only in the same writable database does not prevent a privileged attacker from rewriting the entire chain. Use protected backups or external append-only storage for stronger assurance.

## 15.2 Security controls

- Argon2id password hashing
- Authentication and backend role/permission checks
- GraphQL query depth and complexity limits
- GraphQL request and subscription rate limits
- Input validation and output redaction
- Strict CORS configuration
- HTTPS in production
- CSRF protection where cookie authentication is used
- Secure secret management
- Database and audit file permissions
- Path traversal protection
- Safe symlink handling
- No arbitrary command execution from log data
- Dependency pinning and vulnerability review
- Backups and tested restoration
- Structured application logs without passwords, tokens or unnecessary sensitive data
- Safe error messages without internal stack traces

---

# 16. Reports and exports

Provide reports for:

- File integrity scan history
- File modifications, creations and deletions
- Baseline changes and approvals
- Log source health
- Authentication failures
- Threat detections
- Alerts and resolutions
- Firewall action history
- Audit activity

Support CSV and PDF exports where appropriate. Apply authorization to report generation and ensure exports do not expose secrets or unauthorized file contents.

---

# 17. Testing requirements

## 17.1 Backend unit tests

Use pytest to test:

- SHA-256 hashing, including large files
- Stable-file checks during hashing
- File create/modify/delete detection
- Symlink and path boundary enforcement
- Baseline creation and approval
- Scan scheduling and overlap prevention
- Log parsing for each supported adapter
- Log rotation and truncation
- Duplicate event prevention
- Failed login and brute-force rules
- Privilege escalation detection
- IP normalization
- Alert deduplication
- Authorization checks
- Audit hash-chain verification
- Firewall approval and expiry

## 17.2 GraphQL tests

Test:

- Query results and filtering
- Mutation validation
- Role and permission enforcement
- Pagination and sorting
- Error formatting and redaction
- Query depth and complexity limits
- Subscription authorization
- Subscription event delivery
- Disconnect and reconnect behavior

## 17.3 Frontend tests

Test:

- Login and route protection
- Navigation and role visibility
- Dashboard data loading
- Directory registration and validation
- Scan start and progress
- File event filters
- Log viewer filters
- Threat investigation
- Alert acknowledgement and resolution
- Subscription lifecycle
- Loading, empty and error states
- Responsive behavior

## 17.4 End-to-end acceptance scenarios

**FIM scenario:**

1. Administrator registers a temporary test directory.
2. Application validates the allowed path.
3. Administrator creates a trusted baseline.
4. Test creates, modifies and deletes files.
5. Watchdog triggers verification and the scheduled reconciliation catches missed events.
6. Backend persists the detected events.
7. GraphQL subscription delivers new events to Angular.
8. Analyst investigates an event.
9. Authorized administrator approves or rejects a baseline update.
10. Audit records capture the actions.

**Log monitoring scenario:**

1. Administrator registers a supported test log source.
2. Test fixture supplies synthetic authentication events.
3. Parser normalizes events.
4. Detection engine evaluates configured thresholds.
5. Backend persists security events and any resulting threat/alert.
6. GraphQL subscription delivers authorized live updates.
7. Analyst investigates and resolves the alert.
8. Audit records capture the investigation.

Use temporary directories and synthetic logs. Do not test destructive actions against production systems.

---

# 18. Deployment and operations

## 18.1 Development setup

Frontend:

```bash
cd frontend
npm install
ng serve
```

Backend:

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Use the configured GraphQL URL in the Angular environment. Do not hardcode production addresses in source code.

## 18.2 Production requirements

Provide:

- Angular production build
- Production ASGI server configuration
- Database migrations
- Environment-based configuration
- HTTPS termination
- Secure storage permissions
- Log rotation
- Backup and restore scripts
- Health and readiness checks
- Graceful startup and shutdown
- Monitoring service recovery
- Deployment and upgrade documentation

The Python monitoring engine must run as a managed OS service/daemon or as a properly supervised process. It must not depend on a user keeping Angular open.

For a single-host SQLite deployment, use a single controlled writer strategy and short transactions. If multiple concurrent workers or multiple hosts are required, plan a migration to PostgreSQL and an appropriate shared job/event infrastructure.

---

# 19. Development phases and checkpoints

Build incrementally. At the end of each phase, run tests and leave the repository in a working state.

## Phase 1 — Foundation

- Create `frontend/` and `backend/`.
- Initialize Angular and FastAPI.
- Configure Strawberry GraphQL and Apollo Angular.
- Configure SQLAlchemy and Alembic.
- Create authentication and authorization foundations.
- Create application shell, navigation and design tokens.
- Verify a typed Angular GraphQL query reaches the backend.

**Checkpoint:** Login and authenticated GraphQL query work.

## Phase 2 — File Integrity Monitoring

- Directory registration and path validation
- SHA-256 service
- Baseline creation and versioning
- Scan engine and progress
- Watchdog integration
- Periodic reconciliation
- File event history
- GraphQL queries, mutations and subscriptions

**Checkpoint:** A real test file change appears in the Angular UI and is persisted.

## Phase 3 — Log Monitoring

- Windows and Linux adapters
- Source registration
- Incremental ingestion
- Parsing and normalization
- Authentication event detection
- Privilege-related event detection
- GraphQL queries and subscriptions

**Checkpoint:** Synthetic test events are parsed, stored and displayed.

## Phase 4 — Threat Detection

- Configurable rules
- Threshold and time-window evaluation
- Event correlation
- Threat records
- IP summaries
- Investigation workflow

**Checkpoint:** A test sequence triggers the expected rule and creates an auditable threat.

## Phase 5 — Alerts and Response

- Alert generation and deduplication
- In-app and email notifications
- Alert lifecycle
- Firewall adapters
- Approval workflow
- Expiring block and emergency unblock

**Checkpoint:** A firewall action cannot run without the required approval and is fully audited.

## Phase 6 — Dashboard and Reports

- Live dashboard data
- Charts
- Filters and pagination
- Reports and exports
- System health display

**Checkpoint:** Dashboard uses real GraphQL data and subscriptions.

## Phase 7 — Production hardening

- Security review
- Performance and load testing
- Recovery and backup tests
- Permission review
- Dependency review
- Packaging and deployment documentation

**Checkpoint:** Automated tests pass and a clean installation can be completed using the README.

---

# 20. Instructions for the AI coding agent

Follow these rules throughout implementation:

1. Build a complete working application, not only a visual prototype.
2. Keep `frontend/` and `backend/` as separate root folders.
3. Use Angular for the frontend and Python FastAPI for the backend.
4. Use Strawberry GraphQL and Apollo Angular for application communication.
5. Do not implement REST business endpoints.
6. Use one monolithic backend deployment with modular internal code.
7. Use separate Angular component, page, service, model and GraphQL operation files.
8. Keep Python routes/schema, services, repositories, models and workers separated.
9. Keep business logic out of GraphQL resolvers.
10. Implement actual SHA-256 hashing and filesystem monitoring.
11. Implement real OS-specific log adapters and rule-based detection.
12. Persist data in the database; do not use mock data for production features.
13. Implement authenticated, authorized GraphQL queries, mutations and subscriptions.
14. Generate frontend GraphQL types from the schema/operations.
15. Implement pagination, filtering and sorting.
16. Add input validation and consistent error handling.
17. Ensure background monitoring continues without an open browser.
18. Prevent overlapping scans and safely recover after restart.
19. Keep firewall blocking disabled by default and require approval.
20. Add unit, integration, GraphQL and frontend tests.
21. Document setup, environment variables, permissions, API operations and deployment.
22. Do not leave placeholder buttons, TODO-only business logic or nonfunctional navigation.
23. Do not claim a feature is complete until its implementation and tests exist.
24. At each phase, report files created, commands run, tests passed/failed and known limitations.
25. If an OS capability is unavailable in the development environment, implement the adapter interface and tests with fixtures, clearly mark the integration as unverified on that OS, and do not pretend it is operational.

---

# 21. Final acceptance criteria

The application is complete when:

- An administrator can authenticate and manage authorized users.
- An administrator can register approved directories.
- The backend computes real SHA-256 hashes.
- Trusted baselines can be created, versioned and approved.
- New, modified and deleted files are detected.
- Watchdog events and periodic reconciliation both work.
- Scan jobs run independently of Angular.
- Supported Windows and Linux log adapters are implemented and tested on their respective platforms.
- Authentication and privilege-related events are parsed.
- Configurable detection rules create persisted threats and alerts.
- Angular retrieves application data through GraphQL queries and mutations.
- Real-time events are delivered through authenticated GraphQL subscriptions.
- Role-based authorization is enforced in the backend.
- Audit records are persisted and tamper-evident.
- Firewall actions require explicit approval and are auditable.
- Reports and exports respect permissions.
- Automated tests pass.
- Installation, configuration, backup and deployment instructions are complete.

**Final instruction:** Implement the project phase by phase. Prioritize correctness, security, maintainability and a working end-to-end flow over generating a large volume of files quickly. Do not mark a phase complete until its acceptance criteria and tests have been verified.
