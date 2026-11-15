from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.ordering import parse_order_by
from app.modules.log_monitoring.models import LogSource, SecurityEvent

_LOG_SOURCE_ORDER = {"createdAt": LogSource.created_at, "sourceName": LogSource.source_name, "lastReadAt": LogSource.last_read_at}
_SECURITY_EVENT_ORDER = {
    "normalizedTimestamp": SecurityEvent.normalized_timestamp,
    "severity": SecurityEvent.severity,
    "eventCategory": SecurityEvent.event_category,
}


class LogMonitoringRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_sources(self, order_by: str | None = None, limit: int = 50) -> list[LogSource]:
        statement = (
            select(LogSource)
            .order_by(parse_order_by(order_by, _LOG_SOURCE_ORDER, default="createdAt"))
            .limit(max(1, min(limit, 200)))
        )
        return list(self.session.scalars(statement).all())

    def list_events(self, order_by: str | None = None, limit: int = 100) -> list[SecurityEvent]:
        statement = (
            select(SecurityEvent)
            .order_by(parse_order_by(order_by, _SECURITY_EVENT_ORDER, default="normalizedTimestamp"))
            .limit(max(1, min(limit, 500)))
        )
        return list(self.session.scalars(statement).all())

    def count_events(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(SecurityEvent)) or 0)

    def count_events_today_by_outcome(self, outcome: str) -> int:
        start = datetime_today_start()
        return int(
            self.session.scalar(
                select(func.count())
                .select_from(SecurityEvent)
                .where(SecurityEvent.event_outcome == outcome, SecurityEvent.normalized_timestamp >= start)
            )
            or 0
        )

    def count_events_total_by_outcome(self, outcome: str) -> int:
        return int(
            self.session.scalar(
                select(func.count()).select_from(SecurityEvent).where(SecurityEvent.event_outcome == outcome)
            )
            or 0
        )


def datetime_today_start():
    from datetime import datetime

    from app.core.security import utc_now_naive

    return utc_now_naive().replace(hour=0, minute=0, second=0, microsecond=0)
