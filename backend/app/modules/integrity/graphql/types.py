from datetime import datetime
import strawberry


@strawberry.type
class IntegrityPayload:
    file_path: str
    event_type: str
    severity: str
    checked_at: datetime
    status: str


@strawberry.type
class SecurityAuditPayload:
    alert_id: str
    title: str
    severity: str
    described: str
    generated_at: datetime


@strawberry.input
class IntegrityInput:
    file_path: str
    event_type: str
    directory_name: str
    severity: str


@strawberry.input
class SecurityAuditInput:
    alert_title: str
    alert_description: str
    alert_severity: str
    alert_id: str