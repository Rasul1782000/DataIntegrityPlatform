"""Alert service: creation with deduplication, lifecycle transitions, history."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.alerts.models import Alert, AlertHistory

VALID_ALERT_STATUSES = {"new", "acknowledged", "investigating", "resolved", "false_positive"}


class AlertsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def raise_alert(
        self,
        *,
        alert_type: str,
        title: str,
        description: str | None = None,
        severity: str = "medium",
        deduplication_key: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        actor_id: str | None = None,
    ) -> Alert:
        """Create an alert unless an open alert with the same deduplication key exists."""
        if deduplication_key:
            existing = self.session.scalar(
                select(Alert).where(
                    Alert.deduplication_key == deduplication_key,
                    Alert.status != "resolved",
                    Alert.status != "false_positive",
                )
            )
            if existing is not None:
                return existing

        alert = Alert(
            alert_type=alert_type,
            title=title,
            description=description,
            severity=severity,
            status="new",
            deduplication_key=deduplication_key,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        self.session.add(alert)
        self.session.flush()
        self.session.add(
            AlertHistory(
                alert_id=alert.id,
                actor_id=actor_id,
                action="created",
                note="Alert generated automatically." if deduplication_key else None,
            )
        )
        self.session.commit()
        return alert

    def list_alerts(self, order_by: str | None = None, limit: int = 50) -> list[Alert]:
        from app.core.ordering import parse_order_by
        from sqlalchemy import select as _select

        columns = {"createdAt": Alert.created_at, "severity": Alert.severity, "status": Alert.status}
        statement = (
            _select(Alert)
            .order_by(parse_order_by(order_by, columns, default="createdAt"))
            .limit(max(1, min(limit, 500)))
        )
        return list(self.session.scalars(statement).all())

    def count_critical_open(self) -> int:
        from sqlalchemy import func

        return int(
            self.session.scalar(
                select(func.count())
                .select_from(Alert)
                .where(Alert.severity == "critical", Alert.status != "resolved", Alert.status != "false_positive")
            )
            or 0
        )

    def transition(
        self,
        alert_id: str,
        *,
        action: str,
        new_status: str | None = None,
        note: str | None = None,
        assigned_to: str | None = None,
        actor_id: str | None = None,
    ) -> Alert | None:
        alert = self.session.get(Alert, alert_id)
        if alert is None or new_status not in VALID_ALERT_STATUSES:
            return None
        alert.status = new_status
        if assigned_to is not None:
            alert.assigned_to = assigned_to
        if new_status == "resolved":
            from app.core.security import utc_now_naive

            alert.resolved_at = utc_now_naive()
        self.session.add(AlertHistory(alert_id=alert.id, actor_id=actor_id, action=action, note=note))
        self.session.commit()
        return alert

    def history(self, alert_id: str) -> list[AlertHistory]:
        return list(
            self.session.scalars(
                select(AlertHistory).where(AlertHistory.alert_id == alert_id).order_by(AlertHistory.created_at)
            ).all()
        )
