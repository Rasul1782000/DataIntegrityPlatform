from datetime import datetime

import strawberry

from app.modules.alerts.models import Alert


@strawberry.type
class AlertType:
    id: strawberry.ID
    alert_type: str
    title: str
    description: str | None = None
    severity: str
    status: str
    assigned_to: str | None = None
    deduplication_key: str | None = None
    created_at: datetime | None = None
    resolved_at: datetime | None = None

    @classmethod
    def from_model(cls, model: Alert) -> "AlertType":
        return cls(
            id=strawberry.ID(model.id),
            alert_type=model.alert_type,
            title=model.title,
            description=model.description,
            severity=model.severity,
            status=model.status,
            assigned_to=model.assigned_to,
            deduplication_key=model.deduplication_key,
            created_at=model.created_at,
            resolved_at=model.resolved_at,
        )
