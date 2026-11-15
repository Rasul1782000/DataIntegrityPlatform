from datetime import datetime

import strawberry


@strawberry.type
class DetectionRuleType:
    id: strawberry.ID
    rule_name: str
    description: str | None = None
    rule_type: str
    threshold: int
    time_window_seconds: int
    severity: str
    enabled: bool
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


@strawberry.type
class SuspiciousIPSummary:
    source_ip: str
    associated_usernames: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    failed_authentications: int
    severity: str


@strawberry.type
class ThreatType:
    id: strawberry.ID
    threat_type: str
    severity: str
    status: str
    source_ip: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    related_event_count: int = 0
