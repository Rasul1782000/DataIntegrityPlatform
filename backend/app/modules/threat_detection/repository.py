from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.log_monitoring.models import SecurityEvent


class ThreatRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_rules(self, order_by: str | None = None, limit: int = 50):
        from app.core.ordering import parse_order_by
        from app.modules.threat_detection.models import DetectionRule

        columns = {"createdAt": DetectionRule.created_at, "ruleName": DetectionRule.rule_name}
        statement = (
            select(DetectionRule)
            .order_by(parse_order_by(order_by, columns, default="createdAt"))
            .limit(max(1, min(limit, 200)))
        )
        return list(self.session.scalars(statement).all())

    def count_open_threats(self) -> int:
        from app.modules.threat_detection.models import Threat

        return int(
            self.session.scalar(
                select(func.count()).select_from(Threat).where(Threat.status != "resolved")
            )
            or 0
        )

    def suspicious_ip_summaries(self, limit: int = 100) -> list[dict]:
        """Aggregate suspicious source IPs from real security events."""
        rows = self.session.execute(
            select(
                SecurityEvent.source_ip,
                func.count().label("failed"),
                func.min(SecurityEvent.normalized_timestamp).label("first_seen"),
                func.max(SecurityEvent.normalized_timestamp).label("last_seen"),
            )
            .where(
                SecurityEvent.source_ip.is_not(None),
                SecurityEvent.event_outcome == "failed",
            )
            .group_by(SecurityEvent.source_ip)
            .order_by(func.max(SecurityEvent.normalized_timestamp).desc())
            .limit(max(1, min(limit, 500)))
        ).all()

        summaries: list[dict] = []
        for ip, failed, first_seen, last_seen in rows:
            usernames = self.session.scalars(
                select(SecurityEvent.username)
                .where(SecurityEvent.source_ip == ip, SecurityEvent.username.is_not(None))
                .distinct()
            ).all()
            summaries.append(
                {
                    "source_ip": ip,
                    "associated_usernames": ", ".join(sorted({u for u in usernames if u})) or None,
                    "first_seen_at": first_seen,
                    "last_seen_at": last_seen,
                    "failed_authentications": int(failed),
                    "severity": self._severity_for(int(failed)),
                }
            )
        return summaries

    @staticmethod
    def _severity_for(failed_count: int) -> str:
        if failed_count >= 15:
            return "critical"
        if failed_count >= 5:
            return "high"
        return "medium"
