from datetime import datetime

import strawberry

from app.modules.log_monitoring.models import LogSource, SecurityEvent


@strawberry.type
class LogSourceType:
    id: strawberry.ID
    source_name: str
    source_type: str
    source_path: str
    operating_system: str
    monitoring_enabled: bool
    health_status: str
    last_read_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime | None = None

    @classmethod
    def from_model(cls, model: LogSource) -> "LogSourceType":
        return cls(
            id=strawberry.ID(model.id),
            source_name=model.source_name,
            source_type=model.source_type,
            source_path=model.source_path,
            operating_system=model.operating_system,
            monitoring_enabled=model.monitoring_enabled,
            health_status=model.health_status,
            last_read_at=model.last_read_at,
            last_error=model.last_error,
            created_at=model.created_at,
        )


@strawberry.type
class SecurityEventType:
    id: strawberry.ID
    event_category: str
    event_outcome: str
    severity: str
    status: str
    username: str | None = None
    source_ip: str | None = None
    event_description: str | None = None
    normalized_timestamp: datetime | None = None

    @classmethod
    def from_model(cls, model: SecurityEvent) -> "SecurityEventType":
        return cls(
            id=strawberry.ID(model.id),
            event_category=model.event_category,
            event_outcome=model.event_outcome,
            severity=model.severity,
            status=model.status,
            username=model.username,
            source_ip=model.source_ip,
            event_description=model.event_description,
            normalized_timestamp=model.normalized_timestamp,
        )


@strawberry.input
class RegisterLogSourceInput:
    source_name: str
    source_path: str
    source_type: str = "FILE"
    operating_system: str = "windows"
