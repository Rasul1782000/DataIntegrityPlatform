"""Append-only, tamper-evident audit trail.

Each record embeds the hash of the previous record, so the stored chain can
be verified end-to-end. Note (per requirements): a hash chain inside the same
database is tamper-evident, not tamper-proof; external append-only storage is
recommended for stronger assurance.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditEntry:
    action: str
    entity_type: str
    entity_id: str | None = None
    actor_id: str | None = None
    actor_username: str | None = None
    previous_value: str | None = None
    new_value: str | None = None
    note: str | None = None


def _canonical_payload(entry: AuditEntry, previous_hash: str | None) -> str:
    data = asdict(entry)
    data["previous_record_hash"] = previous_hash
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


class AuditService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, entry: AuditEntry) -> AuditLog:
        last = self.session.scalar(
            select(AuditLog).order_by(AuditLog.timestamp.desc(), AuditLog.id.desc()).limit(1)
        )
        previous_hash = last.record_hash if last is not None else None
        record_hash = hashlib.sha256(_canonical_payload(entry, previous_hash).encode("utf-8")).hexdigest()
        record = AuditLog(
            actor_id=entry.actor_id,
            actor_username=entry.actor_username,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            previous_value=entry.previous_value,
            new_value=entry.new_value,
            note=entry.note,
            previous_record_hash=previous_hash,
            record_hash=record_hash,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list_records(self, order_by: str | None = None, limit: int = 100) -> list[AuditLog]:
        columns = {
            "timestamp": AuditLog.timestamp,
            "action": AuditLog.action,
        }
        from app.core.ordering import parse_order_by

        statement = (
            select(AuditLog)
            .order_by(parse_order_by(order_by, columns, default="timestamp"))
            .limit(max(1, min(limit, 500)))
        )
        return list(self.session.scalars(statement).all())

    def verify_chain(self) -> dict:
        """Recompute the whole chain. Returns {'valid': bool, 'checked': int, 'broken_at': id|None}."""
        records = list(self.session.scalars(select(AuditLog).order_by(AuditLog.timestamp, AuditLog.id)).all())
        previous_hash: str | None = None
        for record in records:
            entry = AuditEntry(
                action=record.action,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                actor_id=record.actor_id,
                actor_username=record.actor_username,
                previous_value=record.previous_value,
                new_value=record.new_value,
                note=record.note,
            )
            expected = hashlib.sha256(_canonical_payload(entry, previous_hash).encode("utf-8")).hexdigest()
            if record.previous_record_hash != previous_hash or record.record_hash != expected:
                logger.warning("Audit chain verification failed at record %s.", record.id)
                return {"valid": False, "checked": len(records), "broken_at": record.id}
            previous_hash = record.record_hash
        return {"valid": True, "checked": len(records), "broken_at": None}
