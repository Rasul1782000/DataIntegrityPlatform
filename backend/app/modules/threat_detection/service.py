"""Threat detection service.

Evaluates configured detection rules over ingested security events and
persists threats. Rules are threshold + time-window based; a threat is
deduplicated per (type, source IP) while it is still open, and each new
threat raises an alert through the alerts module.

Default detection rules are seeded (idempotently) at application startup.
"""

import logging
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import utc_now_naive
from app.modules.alerts.service import AlertsService
from app.modules.log_monitoring.models import SecurityEvent
from app.modules.threat_detection.models import DetectionRule, Threat, ThreatEvent

logger = logging.getLogger(__name__)

DEFAULT_RULES: list[dict] = [
    {
        "rule_name": "Repeated failed login",
        "rule_type": "repeated_failed_login",
        "description": "Several failed authentications from the same source IP within a short window.",
        "threshold": 5,
        "time_window_seconds": 300,
        "severity": "high",
    },
    {
        "rule_name": "Brute-force pattern",
        "rule_type": "brute_force",
        "description": "Sustained failed authentication burst from one source IP.",
        "threshold": 15,
        "time_window_seconds": 600,
        "severity": "critical",
    },
    {
        "rule_name": "Privilege escalation",
        "rule_type": "privilege_escalation",
        "description": "A privilege escalation event (e.g. sudo/admin activity) was observed.",
        "threshold": 1,
        "time_window_seconds": 3600,
        "severity": "high",
    },
    {
        "rule_name": "Failure followed by success",
        "rule_type": "failure_then_success",
        "description": "Successful login after repeated failures from the same source and account.",
        "threshold": 3,
        "time_window_seconds": 600,
        "severity": "high",
    },
    {
        "rule_name": "Multi-account targeting",
        "rule_type": "multi_account_targeting",
        "description": "Failed authentication attempts against several accounts from one source IP.",
        "threshold": 3,
        "time_window_seconds": 600,
        "severity": "high",
    },
]


def ensure_default_rules(session: Session) -> int:
    """Seed default detection rules if none exist. Returns number created."""
    existing = session.scalar(select(func.count()).select_from(DetectionRule)) or 0
    if existing:
        return 0
    session.add_all(DetectionRule(**rule) for rule in DEFAULT_RULES)
    session.commit()
    return len(DEFAULT_RULES)


class ThreatDetectionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.alerts = AlertsService(session)

    # -- evaluation -------------------------------------------------------------

    def evaluate_recent_events(self, lookback_minutes: int = 60) -> int:
        """Run all enabled rules over recent events. Returns threats created."""
        now = utc_now_naive()
        since = now - timedelta(minutes=lookback_minutes)
        events = list(
            self.session.scalars(
                select(SecurityEvent).where(SecurityEvent.normalized_timestamp >= since)
            ).all()
        )
        if not events:
            return 0

        rules = list(self.session.scalars(select(DetectionRule).where(DetectionRule.enabled)).all())
        created = 0
        for rule in rules:
            created += self._apply_rule(rule, events, now)
        self.session.commit()
        return created

    def _apply_rule(self, rule: DetectionRule, events: list[SecurityEvent], now) -> int:
        failed = [e for e in events if e.event_outcome == "failed" and e.event_category == "authentication"]
        created = 0

        if rule.rule_type == "repeated_failed_login":
            created += self._threshold_per_ip(rule, failed, now)
        elif rule.rule_type == "brute_force":
            created += self._threshold_per_ip(rule, failed, now)
        elif rule.rule_type == "privilege_escalation":
            for event in events:
                if event.event_category != "privilege-escalation":
                    continue
                if self._record_threat(rule, event.source_ip, [event], event.normalized_timestamp, event.normalized_timestamp):
                    created += 1
        elif rule.rule_type == "failure_then_success":
            created += self._failure_then_success(rule, events, now)
        elif rule.rule_type == "multi_account_targeting":
            created += self._multi_account(rule, failed, now)
        return created

    def _threshold_per_ip(self, rule: DetectionRule, failed: list[SecurityEvent], now) -> int:
        by_ip: dict[str, list[SecurityEvent]] = defaultdict(list)
        for event in failed:
            if event.source_ip:
                by_ip[event.source_ip].append(event)

        created = 0
        for ip, ip_events in by_ip.items():
            ip_events.sort(key=lambda e: e.normalized_timestamp)
            window_start = now - timedelta(seconds=rule.time_window_seconds)
            recent = [e for e in ip_events if e.normalized_timestamp >= window_start]
            if len(recent) >= rule.threshold:
                first = recent[0].normalized_timestamp
                last = recent[-1].normalized_timestamp
                if self._record_threat(rule, ip, recent, first, last):
                    created += 1
        return created

    def _failure_then_success(self, rule: DetectionRule, events: list[SecurityEvent], now) -> int:
        successes = [e for e in events if e.event_outcome == "success" and e.event_category == "authentication"]
        created = 0
        for success in successes:
            if not success.source_ip:
                continue
            window_start = success.normalized_timestamp - timedelta(seconds=rule.time_window_seconds)
            prior_failures = [
                e
                for e in events
                if e.event_outcome == "failed"
                and e.source_ip == success.source_ip
                and e.username == success.username
                and window_start <= e.normalized_timestamp <= success.normalized_timestamp
            ]
            if len(prior_failures) >= rule.threshold:
                first = prior_failures[0].normalized_timestamp
                if self._record_threat(rule, success.source_ip, [*prior_failures, success], first, success.normalized_timestamp):
                    created += 1
        return created

    def _multi_account(self, rule: DetectionRule, failed: list[SecurityEvent], now) -> int:
        by_ip: dict[str, set[str]] = defaultdict(set)
        ip_events: dict[str, list[SecurityEvent]] = defaultdict(list)
        window_start = now - timedelta(seconds=rule.time_window_seconds)
        for event in failed:
            if event.source_ip and event.username and event.normalized_timestamp >= window_start:
                by_ip[event.source_ip].add(event.username)
                ip_events[event.source_ip].append(event)

        created = 0
        for ip, usernames in by_ip.items():
            if len(usernames) >= rule.threshold:
                related = ip_events[ip]
                first = min(e.normalized_timestamp for e in related)
                last = max(e.normalized_timestamp for e in related)
                if self._record_threat(rule, ip, related, first, last):
                    created += 1
        return created

    def _record_threat(
        self,
        rule: DetectionRule,
        source_ip: str | None,
        related: list[SecurityEvent],
        first_seen,
        last_seen,
    ) -> bool:
        """Create or update a threat. Returns True when a new threat was created."""
        existing = self.session.scalar(
            select(Threat).where(
                Threat.threat_type == rule.rule_type,
                Threat.source_ip == source_ip,
                Threat.status != "resolved",
            )
        )
        if existing is not None:
            existing.last_seen_at = max(existing.last_seen_at, last_seen)
            self._link_events(existing, related)
            return False

        threat = Threat(
            threat_type=rule.rule_type,
            severity=rule.severity,
            status="open",
            source_ip=source_ip,
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            related_event_count=0,
            detection_rule_id=rule.id,
        )
        self.session.add(threat)
        self.session.flush()
        self._link_events(threat, related)
        self.alerts.raise_alert(
            alert_type=f"THREAT_{rule.rule_type.upper()}",
            title=f"{rule.rule_name}: {source_ip or 'unknown source'}",
            description=f"{rule.description} Observed {len(related)} related event(s).",
            severity=rule.severity,
            deduplication_key=f"{rule.rule_type}:{source_ip}:{first_seen.date().isoformat()}",
            related_entity_type="threat",
            related_entity_id=threat.id,
        )
        logger.info("Threat detected: %s (%s)", rule.rule_name, source_ip)
        return True

    def _link_events(self, threat: Threat, related: list[SecurityEvent]) -> None:
        existing_ids = set(
            self.session.scalars(select(ThreatEvent.security_event_id).where(ThreatEvent.threat_id == threat.id)).all()
        )
        new_links = [
            ThreatEvent(threat_id=threat.id, security_event_id=event.id)
            for event in related
            if event.id not in existing_ids
        ]
        if new_links:
            self.session.add_all(new_links)
        threat.related_event_count = self.session.scalar(
            select(func.count()).select_from(ThreatEvent).where(ThreatEvent.threat_id == threat.id)
        )
