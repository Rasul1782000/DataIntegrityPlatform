from datetime import datetime

import strawberry


@strawberry.type
class SecurityAuditPayload:
    alert_id: str
    title: str
    severity: str
    described: str
    generated_at: datetime


@strawberry.input
class SecurityAuditInput:
    alert_title: str
    alert_description: str
    alert_severity: str
    alert_id: str