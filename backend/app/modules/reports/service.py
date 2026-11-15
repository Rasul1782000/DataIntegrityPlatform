"""Report generation: real aggregates written to CSV under storage/reports."""

import csv
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ordering import parse_order_by
from app.modules.alerts.models import Alert
from app.modules.integrity.models import FileIntegrityEvent, MonitoredDirectory
from app.modules.log_monitoring.models import SecurityEvent
from app.modules.reports.models import Report
from app.modules.threat_detection.models import Threat

logger = logging.getLogger(__name__)

REPORT_TYPES = {"FILE_INTEGRITY_SUMMARY", "AUTH_ACTIVITY", "ALERT_SUMMARY", "THREAT_SUMMARY"}


class ReportsService:
    def __init__(self, session: Session, storage_dir: Path) -> None:
        self.session = session
        self.storage_dir = storage_dir

    def generate(self, report_type: str) -> Report:
        report_type = report_type.strip().casefold()
        matched = {t.casefold(): t for t in REPORT_TYPES}.get(report_type)
        if matched is None:
            raise ValueError(f"Unsupported report type. Choose one of: {', '.join(sorted(REPORT_TYPES))}")

        builder = {
            "file_integrity_summary": self._file_integrity_rows,
            "auth_activity": self._auth_rows,
            "alert_summary": self._alert_rows,
            "threat_summary": self._threat_rows,
        }[matched.casefold()]

        headers, rows = builder()
        file_path = self._write_csv(matched, headers, rows)
        report = Report(
            title=matched.replace("_", " ").title(),
            report_type=matched,
            record_count=len(rows),
            format="CSV",
            file_path=str(file_path),
        )
        self.session.add(report)
        self.session.commit()
        return report

    def list_reports(self, order_by: str | None = None, limit: int = 50) -> list[Report]:
        columns = {"generatedAt": Report.generated_at, "title": Report.title}
        statement = (
            select(Report)
            .order_by(parse_order_by(order_by, columns, default="generatedAt"))
            .limit(max(1, min(limit, 500)))
        )
        return list(self.session.scalars(statement).all())

    # -- builders ---------------------------------------------------------------

    def _file_integrity_rows(self) -> tuple[list[str], list[list]]:
        rows: list[list] = []
        directories = list(self.session.scalars(select(MonitoredDirectory)).all())
        event_counts = Counter(
            self.session.scalars(select(FileIntegrityEvent.event_type)).all()
        )
        rows.append(["Monitored directories", str(len(directories))])
        for event_type, count in sorted(event_counts.items()):
            rows.append([f"Events: {event_type}", str(count)])
        return ["metric", "value"], rows

    def _auth_rows(self) -> tuple[list[str], list[list]]:
        outcomes = Counter(
            self.session.scalars(
                select(SecurityEvent.event_outcome).where(SecurityEvent.event_category == "authentication")
            ).all()
        )
        top_ips = Counter(
            self.session.scalars(
                select(SecurityEvent.source_ip).where(
                    SecurityEvent.source_ip.is_not(None), SecurityEvent.event_outcome == "failed"
                )
            ).all()
        )
        rows = [
            ["Successful authentications", str(outcomes.get("success", 0))],
            ["Failed authentications", str(outcomes.get("failed", 0))],
        ]
        for ip, count in top_ips.most_common(10):
            rows.append([f"Top failing IP: {ip}", str(count)])
        return ["metric", "value"], rows

    def _alert_rows(self) -> tuple[list[str], list[list]]:
        rows: list[list] = []
        for severity, count in Counter(
            self.session.scalars(select(Alert.severity)).all()
        ).items():
            rows.append([f"Alerts severity={severity}", str(count)])
        for status, count in Counter(
            self.session.scalars(select(Alert.status)).all()
        ).items():
            rows.append([f"Alerts status={status}", str(count)])
        return ["metric", "value"], rows

    def _threat_rows(self) -> tuple[list[str], list[list]]:
        rows: list[list] = []
        for threat_type, count in Counter(
            self.session.scalars(select(Threat.threat_type)).all()
        ).items():
            rows.append([f"Threats: {threat_type}", str(count)])
        for status, count in Counter(
            self.session.scalars(select(Threat.status)).all()
        ).items():
            rows.append([f"Threats status={status}", str(count)])
        return ["metric", "value"], rows

    # -- output -------------------------------------------------------------------

    def _write_csv(self, report_type: str, headers: list[str], rows: list[list]) -> Path:
        reports_dir = self.storage_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        file_path = reports_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{report_type}.csv"
        with file_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        return file_path
