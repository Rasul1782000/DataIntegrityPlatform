import strawberry
from strawberry.types import Info

from app.modules.reports.graphql.types import ReportType
from app.modules.reports.service import ReportsService


@strawberry.type
class ReportQueries:
    @strawberry.field
    def reports(self, info: Info, order_by: str | None = "generatedAt_DESC", limit: int = 50) -> list[ReportType]:
        storage_dir = info.context.settings.storage_dir
        reports = ReportsService(info.context.db, storage_dir).list_reports(order_by=order_by, limit=limit)
        return [ReportType.from_model(report) for report in reports]
