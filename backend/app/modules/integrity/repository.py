from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.ordering import parse_order_by
from app.modules.integrity.models import FileBaseline, FileIntegrityEvent, MonitoredDirectory, ScanRun

_EVENT_ORDER_COLUMNS = {
    "detectedAt": FileIntegrityEvent.detected_at,
    "relativePath": FileIntegrityEvent.relative_path,
    "severity": FileIntegrityEvent.severity,
    "eventType": FileIntegrityEvent.event_type,
}


class IntegrityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # -- directories ---------------------------------------------------------

    def list_directories(self) -> list[MonitoredDirectory]:
        return list(self.session.scalars(select(MonitoredDirectory).order_by(MonitoredDirectory.name)).all())

    def get_directory(self, directory_id: str) -> MonitoredDirectory | None:
        return self.session.get(MonitoredDirectory, directory_id)

    def get_directory_by_path(self, canonical_path: str) -> MonitoredDirectory | None:
        return self.session.scalar(
            select(MonitoredDirectory).where(MonitoredDirectory.canonical_path == canonical_path)
        )

    def add_directory(self, directory: MonitoredDirectory) -> MonitoredDirectory:
        self.session.add(directory)
        self.session.flush()
        return directory

    def count_enabled_directories(self) -> int:
        return int(
            self.session.scalar(
                select(func.count()).select_from(MonitoredDirectory).where(MonitoredDirectory.monitoring_enabled)
            )
            or 0
        )

    # -- scan runs -----------------------------------------------------------

    def get_running_scan(self, directory_id: str) -> ScanRun | None:
        return self.session.scalar(
            select(ScanRun).where(ScanRun.directory_id == directory_id, ScanRun.status == "RUNNING")
        )

    def add_scan(self, scan: ScanRun) -> ScanRun:
        self.session.add(scan)
        self.session.flush()
        return scan

    def last_completed_scan(self) -> ScanRun | None:
        return self.session.scalar(
            select(ScanRun)
            .where(ScanRun.status == "COMPLETED", ScanRun.completed_at.is_not(None))
            .order_by(ScanRun.completed_at.desc())
            .limit(1)
        )

    def last_completed_scan_for_directory(self, directory_id: str) -> ScanRun | None:
        return self.session.scalar(
            select(ScanRun)
            .where(
                ScanRun.directory_id == directory_id,
                ScanRun.status == "COMPLETED",
                ScanRun.completed_at.is_not(None),
            )
            .order_by(ScanRun.completed_at.desc())
            .limit(1)
        )

    # -- baselines -----------------------------------------------------------

    def baseline_entries(self, directory_id: str) -> list[FileBaseline]:
        """Latest baseline version for the directory."""
        latest_version = self.session.scalar(
            select(func.max(FileBaseline.baseline_version)).where(FileBaseline.directory_id == directory_id)
        )
        if latest_version is None:
            return []
        return list(
            self.session.scalars(
                select(FileBaseline).where(
                    FileBaseline.directory_id == directory_id,
                    FileBaseline.baseline_version == latest_version,
                )
            ).all()
        )

    def baseline_count(self) -> int:
        latest = (
            select(FileBaseline.directory_id, func.max(FileBaseline.baseline_version).label("version"))
            .group_by(FileBaseline.directory_id)
            .subquery()
        )
        return int(
            self.session.scalar(
                select(func.count())
                .select_from(FileBaseline)
                .join(
                    latest,
                    (FileBaseline.directory_id == latest.c.directory_id)
                    & (FileBaseline.baseline_version == latest.c.version),
                )
            )
            or 0
        )

    def add_baseline_entries(self, entries: list[FileBaseline]) -> None:
        self.session.add_all(entries)
        self.session.flush()

    # -- events --------------------------------------------------------------

    def add_events(self, events: list[FileIntegrityEvent]) -> None:
        self.session.add_all(events)
        self.session.flush()

    def recent_events(self, limit: int, order_by: str | None = None) -> list[tuple[FileIntegrityEvent, str]]:
        statement = (
            select(FileIntegrityEvent, MonitoredDirectory.name)
            .join(MonitoredDirectory, FileIntegrityEvent.directory_id == MonitoredDirectory.id)
            .order_by(parse_order_by(order_by, _EVENT_ORDER_COLUMNS, default="detectedAt"))
            .limit(max(1, min(limit, 200)))
        )
        return [(event, name) for event, name in self.session.execute(statement).all()]

    def count_events_today(self, event_type: str) -> int:
        from app.core.security import utc_now_naive

        start = utc_now_naive().replace(hour=0, minute=0, second=0, microsecond=0)
        return int(
            self.session.scalar(
                select(func.count())
                .select_from(FileIntegrityEvent)
                .where(
                    FileIntegrityEvent.event_type == event_type,
                    FileIntegrityEvent.detected_at >= start,
                )
            )
            or 0
        )
