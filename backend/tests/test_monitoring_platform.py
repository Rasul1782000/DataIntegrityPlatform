"""Monitoring platform tests.

The GraphQL contract test is the acceptance gate: it executes exactly the
operations the Angular services send and fails on any schema mismatch.
"""

import time

from fastapi.testclient import TestClient

from tests.conftest import graphql


# ---------------------------------------------------------------------------
# The exact operations the frontend sends (must match the schema)
# ---------------------------------------------------------------------------

FRONTEND_QUERIES: dict[str, str] = {
    "dashboardSummary": """
        query GetDashboardSummary {
          dashboardSummary {
            totalMonitoredDirectories totalMonitoredFiles modifiedFilesToday
            addedFilesToday deletedFilesToday totalLogEvents failedLoginAttempts
            activeThreats criticalAlerts lastSuccessfulScan
          }
        }""",
    "monitoredDirectories": """
        query GetMonitoredDirectories {
          monitoredDirectories { id name canonicalPath monitoringEnabled scanFrequency }
        }""",
    "fileIntegrityEvents": """
        query GetRecentFileEvents {
          fileIntegrityEvents(orderBy: "detectedAt_DESC", limit: 20) {
            id directoryName relativePath eventType previousHash currentHash
            severity detectedAt status
          }
        }""",
    "fileBaselinesAggregate": """
        query GetBaselinesCount { fileBaselinesAggregate { count } }""",
    "logSources": """
        query GetLogSources {
          logSources(orderBy: "createdAt_DESC", limit: 50) {
            id sourceName sourceType sourcePath healthStatus lastReadAt
          }
        }""",
    "securityEvents": """
        query GetSecurityEvents {
          securityEvents(orderBy: "normalizedTimestamp_DESC", limit: 100) {
            id eventCategory severity eventDescription normalizedTimestamp status
          }
        }""",
    "detectionRules": """
        query GetDetectionRules {
          detectionRules(orderBy: "createdAt_DESC", limit: 50) {
            id ruleName ruleType severity threshold enabled
          }
        }""",
    "suspiciousIPs": """
        query GetSuspiciousIPs {
          suspiciousIPs(orderBy: "lastSeenAt_DESC", limit: 100) {
            sourceIp associatedUsernames firstSeenAt lastSeenAt failedAuthentications severity
          }
        }""",
    "alerts": """
        query GetAlerts {
          alerts(orderBy: "createdAt_DESC", limit: 50) {
            id alertType title description severity status assignedTo
            deduplicationKey createdAt resolvedAt
          }
        }""",
    "auditLogs": """
        query GetAuditLogs {
          auditLogs(orderBy: "timestamp_DESC", limit: 100) {
            id actorId actorUsername action entityType entityId previousValue
            newValue note timestamp previousRecordHash recordHash
          }
        }""",
    "reports": """
        query GetReports {
          reports(orderBy: "generatedAt_DESC", limit: 50) {
            id title type generatedAt recordCount format
          }
        }""",
    "users": """
        query GetUsers {
          users(orderBy: "createdAt_DESC", limit: 100) {
            id username email fullName role isActive lastLogin createdAt
          }
        }""",
}


def test_frontend_graphql_contract(client: TestClient) -> None:
    """Every frontend query must resolve without errors."""
    for name, query in FRONTEND_QUERIES.items():
        response = graphql(client, query)
        assert response.status_code == 200, name
        payload = response.json()
        assert "errors" not in payload, f"{name}: {payload.get('errors')}"
        assert name in payload["data"], f"{name} missing from data"
    # Detection rules are seeded at startup (config, not fabricated data).
    rules = client.post("/graphql", json={"query": FRONTEND_QUERIES["detectionRules"]}).json()
    assert len(rules["data"]["detectionRules"]) >= 5


# ---------------------------------------------------------------------------
# File integrity end-to-end
# ---------------------------------------------------------------------------

REGISTER = """
    mutation Register($input: RegisterDirectoryInput!) {
      registerDirectory(input: $input) { directory { id canonicalPath } error { message } }
    }"""
SCAN = """
    mutation StartScan($id: ID!) {
      startIntegrityScan(directoryId: $id) { scan { id status filesExamined errorsCount } error { message } }
    }"""


def _data(client: TestClient, query: str, variables: dict | None = None) -> dict:
    response = graphql(client, query, variables)
    payload = response.json()
    assert "errors" not in payload, payload.get("errors")
    return payload["data"]


def test_file_integrity_detects_create_modify_delete(client: TestClient, tmp_path) -> None:
    directory = tmp_path / "watched"
    directory.mkdir()
    (directory / "keep.txt").write_text("original")

    data = _data(client, REGISTER, {"input": {"name": "Watched", "path": str(directory), "recursive": True}})
    directory_id = data["registerDirectory"]["directory"]["id"]
    assert data["registerDirectory"]["error"] is None

    # Initial scan builds the trusted baseline and raises no events.
    scan = _data(client, SCAN, {"id": directory_id})["startIntegrityScan"]["scan"]
    assert scan["status"] == "COMPLETED"

    # Baselines exist now.
    count = _data(client, FRONTEND_QUERIES["fileBaselinesAggregate"])["fileBaselinesAggregate"]["count"]
    assert count == 1

    # Second clean scan: no events.
    _data(client, SCAN, {"id": directory_id})
    events = _data(client, FRONTEND_QUERIES["fileIntegrityEvents"])["fileIntegrityEvents"]
    assert events == []

    # Create a new file, modify a baseline file, then delete a baseline file.
    (directory / "new.txt").write_text("hello")
    (directory / "keep.txt").write_text("tampered")
    _data(client, SCAN, {"id": directory_id})  # CREATED(new) + MODIFIED(keep)
    (directory / "keep.txt").unlink()
    _data(client, SCAN, {"id": directory_id})  # DELETED(keep - it is in the baseline)

    events = _data(client, FRONTEND_QUERIES["fileIntegrityEvents"])["fileIntegrityEvents"]
    types = {event["eventType"] for event in events}
    assert {"CREATED", "MODIFIED", "DELETED"} <= types
    assert events[0]["directoryName"] == "Watched"

    # Dashboard reflects real data.
    summary = _data(client, FRONTEND_QUERIES["dashboardSummary"])["dashboardSummary"]
    assert summary["totalMonitoredDirectories"] == 1
    assert summary["modifiedFilesToday"] >= 1
    assert summary["addedFilesToday"] >= 1
    assert summary["deletedFilesToday"] >= 1
    assert summary["lastSuccessfulScan"] is not None


def test_duplicate_directory_registration_rejected(client: TestClient, tmp_path) -> None:
    directory = tmp_path / "dupe"
    directory.mkdir()
    first = _data(client, REGISTER, {"input": {"name": "A", "path": str(directory)}})
    assert first["registerDirectory"]["error"] is None
    second = _data(client, REGISTER, {"input": {"name": "B", "path": str(directory)}})
    assert second["registerDirectory"]["error"]["message"] == "This path is already being monitored."


# ---------------------------------------------------------------------------
# Log monitoring -> threat detection -> alerts
# ---------------------------------------------------------------------------

REGISTER_LOG = """
    mutation RegisterLog($input: RegisterLogSourceInput!) {
      registerLogSource(input: $input) { source { id sourceName healthStatus } error }
    }"""
INGEST = """
    mutation Ingest($id: ID!) { ingestLogSource(sourceId: $id) { storedEvents error } }"""


def test_log_ingestion_pipelines_to_threats_and_alerts(client: TestClient, tmp_path) -> None:
    from app.modules.threat_detection.service import ThreatDetectionService

    log_file = tmp_path / "auth.log"
    log_file.write_text(
        "Failed password for alice from 203.0.113.50 port 41000 ssh2\n"
        "Failed password for bob from 203.0.113.50 port 41001 ssh2\n"
        "Failed password for alice from 203.0.113.50 port 41002 ssh2\n"
        "Failed password for admin from 203.0.113.50 port 41003 ssh2\n"
        "Failed password for root from 203.0.113.50 port 41004 ssh2\n"
        "Accepted password for alice from 203.0.113.50 port 41005 ssh2\n"
        "sudo: alice : TTY=pts/0 ; PWD=/root ; COMMAND=/bin/sh\n"
    )

    data = _data(
        client,
        REGISTER_LOG,
        {"input": {"sourceName": "test auth log", "sourcePath": str(log_file), "sourceType": "FILE"}},
    )
    assert data["registerLogSource"]["error"] is None
    source_id = data["registerLogSource"]["source"]["id"]

    result = _data(client, INGEST, {"id": source_id})["ingestLogSource"]
    assert result["storedEvents"] == 7
    assert result["error"] is None

    # Incremental: re-ingest stores nothing new (duplicate prevention).
    assert _data(client, INGEST, {"id": source_id})["ingestLogSource"]["storedEvents"] == 0

    events = _data(client, FRONTEND_QUERIES["securityEvents"])["securityEvents"]
    assert len(events) == 7
    assert any(event["eventCategory"] == "privilege-escalation" for event in events)
    assert any(event["eventCategory"] == "authentication" for event in events)

    ips = _data(client, FRONTEND_QUERIES["suspiciousIPs"])["suspiciousIPs"]
    assert len(ips) == 1
    assert ips[0]["sourceIp"] == "203.0.113.50"
    assert ips[0]["failedAuthentications"] == 5
    assert "alice" in ips[0]["associatedUsernames"]

    # Detection rules run over the new events.
    ThreatDetectionService(client.app.state.session_factory().__enter__()).evaluate_recent_events()
    summary = _data(client, FRONTEND_QUERIES["dashboardSummary"])["dashboardSummary"]
    assert summary["activeThreats"] >= 1
    assert summary["totalLogEvents"] == 7
    assert summary["failedLoginAttempts"] >= 5

    alerts = _data(client, FRONTEND_QUERIES["alerts"])["alerts"]
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    ack = _data(client, "mutation($id: ID!){ acknowledgeAlert(alertId: $id){ alert { status } } }", {"id": alert_id})
    assert ack["acknowledgeAlert"]["alert"]["status"] == "acknowledged"
    resolved = _data(
        client, "mutation($id: ID!){ resolveAlert(alertId: $id){ alert { status resolvedAt } } }", {"id": alert_id}
    )
    assert resolved["resolveAlert"]["alert"]["status"] == "resolved"
    assert resolved["resolveAlert"]["alert"]["resolvedAt"] is not None


def test_audit_trail_records_and_verifies_chain(client: TestClient, tmp_path) -> None:
    from app.modules.audit.service import AuditEntry, AuditService

    session_factory = client.app.state.session_factory
    with session_factory() as session:
        service = AuditService(session)
        service.record(AuditEntry(action="directory_registered", entity_type="monitored_directory", new_value="alpha"))
        session.commit()
        service.record(AuditEntry(action="scan_started", entity_type="scan_run", new_value="beta"))
        session.commit()

        result = service.verify_chain()
        assert result["valid"] is True
        assert result["checked"] >= 2

        # Tampering with one record breaks the chain verification.
        first = service.list_records(limit=1)[0]
        session.execute(
            __import__("sqlalchemy").text("UPDATE audit_logs SET action = 'tampered' WHERE id = :id"),
            {"id": first.id},
        )
        session.commit()
        session.expire_all()  # bypass the identity map; production uses fresh sessions
        assert service.verify_chain()["valid"] is False


def test_report_generation(client: TestClient) -> None:
    data = _data(client, 'mutation { generateReport(reportType: "FILE_INTEGRITY_SUMMARY") { report { title recordCount format } error } }')
    report = data["generateReport"]["report"]
    assert report is not None and report["format"] == "CSV"
    listing = _data(client, FRONTEND_QUERIES["reports"])["reports"]
    assert len(listing) >= 1
