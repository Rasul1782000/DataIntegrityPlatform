import strawberry
from strawberry.types import Info

from app.modules.log_monitoring.graphql.types import LogSourceType, RegisterLogSourceInput
from app.modules.log_monitoring.service import LogMonitoringService


@strawberry.type
class LogSourceMutationPayload:
    source: LogSourceType | None = None
    error: str | None = None


@strawberry.type
class IngestLogSourcePayload:
    source_id: strawberry.ID
    stored_events: int
    error: str | None = None


@strawberry.type
class LogMonitoringMutations:
    @strawberry.mutation
    def register_log_source(self, info: Info, input: RegisterLogSourceInput) -> LogSourceMutationPayload:
        try:
            source = LogMonitoringService(info.context.db).register_source(
                source_name=input.source_name,
                source_type=input.source_type,
                source_path=input.source_path,
                operating_system=input.operating_system,
            )
        except ValueError as error:
            return LogSourceMutationPayload(error=str(error))
        return LogSourceMutationPayload(source=LogSourceType.from_model(source))

    @strawberry.mutation
    def ingest_log_source(self, info: Info, source_id: strawberry.ID) -> IngestLogSourcePayload:
        stored = LogMonitoringService(info.context.db).ingest_source(str(source_id))
        return IngestLogSourcePayload(source_id=source_id, stored_events=stored)
