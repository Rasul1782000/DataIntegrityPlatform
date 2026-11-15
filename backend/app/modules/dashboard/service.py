"""Dashboard aggregates computed from persisted data only."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.alerts.service import AlertsService
from app.modules.integrity.repository import IntegrityRepository
from app.modules.log_monitoring.repository import LogMonitoringRepository
from app.modules.threat_detection.repository import ThreatRepository


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.integrity = IntegrityRepository(session)
        self.logs = LogMonitoringRepository(session)
        self.threats = ThreatRepository(session)
        self.alerts = AlertsService(session)

    def summary(self) -> dict:
        return {
            "total_monitored_directories": self.integrity.count_enabled_directories(),
            "total_monitored_files": self.integrity.baseline_count(),
            "modified_files_today": self.integrity.count_events_today("MODIFIED"),
            "added_files_today": self.integrity.count_events_today("CREATED"),
            "deleted_files_today": self.integrity.count_events_today("DELETED"),
            "total_log_events": self.logs.count_events(),
            "failed_login_attempts": self.logs.count_events_total_by_outcome("failed"),
            "successful_login_attempts": self.logs.count_events_total_by_outcome("success"),
            "active_threats": self.threats.count_open_threats(),
            "critical_alerts": self.alerts.count_critical_open(),
            "last_successful_scan": self._last_successful_scan(),
        }

    def _last_successful_scan(self) -> datetime | None:
        scan = self.integrity.last_completed_scan()
        return scan.completed_at if scan is not None else None
