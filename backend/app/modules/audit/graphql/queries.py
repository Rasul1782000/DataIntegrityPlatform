import strawberry
from strawberry.types import Info

from app.modules.audit.graphql.types import AuditLogType
from app.modules.audit.service import AuditService


@strawberry.type
class AuditChainStatus:
    valid: bool
    checked: int
    broken_at: str | None = None


@strawberry.type
class AuditQueries:
    @strawberry.field
    def audit_logs(self, info: Info, order_by: str | None = "timestamp_DESC", limit: int = 100) -> list[AuditLogType]:
        records = AuditService(info.context.db).list_records(order_by=order_by, limit=limit)
        return [AuditLogType.from_model(record) for record in records]

    @strawberry.field
    def audit_chain_status(self, info: Info) -> AuditChainStatus:
        result = AuditService(info.context.db).verify_chain()
        return AuditChainStatus(**result)
