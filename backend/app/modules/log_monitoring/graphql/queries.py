import strawberry
from strawberry.types import Info

from app.modules.log_monitoring.graphql.types import LogSourceType, SecurityEventType
from app.modules.log_monitoring.repository import LogMonitoringRepository


@strawberry.type
class LogMonitoringQueries:
    @strawberry.field
    def log_sources(self, info: Info, order_by: str | None = "createdAt_DESC", limit: int = 50) -> list[LogSourceType]:
        sources = LogMonitoringRepository(info.context.db).list_sources(order_by=order_by, limit=limit)
        return [LogSourceType.from_model(source) for source in sources]

    @strawberry.field
    def security_events(
        self, info: Info, order_by: str | None = "normalizedTimestamp_DESC", limit: int = 100
    ) -> list[SecurityEventType]:
        events = LogMonitoringRepository(info.context.db).list_events(order_by=order_by, limit=limit)
        return [SecurityEventType.from_model(event) for event in events]
