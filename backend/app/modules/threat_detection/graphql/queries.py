import strawberry
from strawberry.types import Info

from app.modules.threat_detection.graphql.types import DetectionRuleType, SuspiciousIPSummary
from app.modules.threat_detection.repository import ThreatRepository


@strawberry.type
class ThreatDetectionQueries:
    @strawberry.field
    def detection_rules(self, info: Info, order_by: str | None = "createdAt_DESC", limit: int = 50) -> list[DetectionRuleType]:
        rules = ThreatRepository(info.context.db).list_rules(order_by=order_by, limit=limit)
        return [
            DetectionRuleType(
                id=strawberry.ID(rule.id),
                rule_name=rule.rule_name,
                description=rule.description,
                rule_type=rule.rule_type,
                threshold=rule.threshold,
                time_window_seconds=rule.time_window_seconds,
                severity=rule.severity,
                enabled=rule.enabled,
                version=rule.version,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
            )
            for rule in rules
        ]

    @strawberry.field
    def suspicious_i_ps(self, info: Info, order_by: str | None = "lastSeenAt_DESC", limit: int = 100) -> list[SuspiciousIPSummary]:
        del order_by  # aggregation already orders by last seen
        summaries = ThreatRepository(info.context.db).suspicious_ip_summaries(limit=limit)
        return [SuspiciousIPSummary(**summary) for summary in summaries]
