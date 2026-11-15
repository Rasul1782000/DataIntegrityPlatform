from datetime import datetime

import strawberry

from app.modules.reports.models import Report


@strawberry.type
class ReportType:
    id: strawberry.ID
    title: str
    type: str
    generated_at: datetime | None = None
    record_count: int = 0
    format: str = "CSV"

    @classmethod
    def from_model(cls, model: Report) -> "ReportType":
        return cls(
            id=strawberry.ID(model.id),
            title=model.title,
            type=model.report_type,
            generated_at=model.generated_at,
            record_count=model.record_count,
            format=model.format,
        )
