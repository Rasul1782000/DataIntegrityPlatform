from datetime import datetime

import strawberry

from app.modules.audit.models import AuditLog


@strawberry.type
class AuditLogType:
    id: strawberry.ID
    actor_id: str | None = None
    actor_username: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    previous_value: str | None = None
    new_value: str | None = None
    note: str | None = None
    timestamp: datetime | None = None
    previous_record_hash: str | None = None
    record_hash: str | None = None

    @classmethod
    def from_model(cls, model: AuditLog) -> "AuditLogType":
        return cls(
            id=strawberry.ID(model.id),
            actor_id=model.actor_id,
            actor_username=model.actor_username,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            previous_value=model.previous_value,
            new_value=model.new_value,
            note=model.note,
            timestamp=model.timestamp,
            previous_record_hash=model.previous_record_hash,
            record_hash=model.record_hash,
        )
