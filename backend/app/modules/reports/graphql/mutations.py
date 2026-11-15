import strawberry
from strawberry.types import Info

from app.modules.reports.graphql.types import ReportType
from app.modules.reports.service import REPORT_TYPES, ReportsService


@strawberry.type
class GenerateReportPayload:
    report: ReportType | None = None
    error: str | None = None


@strawberry.type
class ReportMutations:
    @strawberry.mutation
    def generate_report(self, info: Info, report_type: str) -> GenerateReportPayload:
        try:
            report = ReportsService(info.context.db, info.context.settings.storage_dir).generate(report_type)
        except ValueError as error:
            return GenerateReportPayload(error=str(error))
        return GenerateReportPayload(report=ReportType.from_model(report))
