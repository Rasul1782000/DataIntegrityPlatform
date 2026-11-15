import strawberry
from strawberry.types import Info

from app.modules.integrity.graphql.types import (
    FileBaselinesAggregate,
    FileIntegrityEventType,
    MonitoredDirectoryType,
)
from app.modules.integrity.repository import IntegrityRepository
from app.modules.integrity.service import IntegrityService


@strawberry.type
class IntegrityQueries:
    @strawberry.field
    def monitored_directories(self, info: Info) -> list[MonitoredDirectoryType]:
        service = IntegrityService(info.context.db)
        return [MonitoredDirectoryType.from_model(d) for d in service.repo.list_directories()]

    @strawberry.field
    def file_integrity_events(
        self, info: Info, order_by: str | None = "detectedAt_DESC", limit: int = 20
    ) -> list[FileIntegrityEventType]:
        # Keep resolvers thin: the repository owns the query and ordering.
        events = IntegrityRepository(info.context.db).recent_events(limit=limit, order_by=order_by)
        return [FileIntegrityEventType.from_model(event, name) for event, name in events]

    @strawberry.field
    def file_baselines_aggregate(self, info: Info) -> FileBaselinesAggregate:
        return FileBaselinesAggregate(count=IntegrityRepository(info.context.db).baseline_count())
