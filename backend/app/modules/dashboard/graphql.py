from datetime import datetime

import strawberry
from strawberry.types import Info

from app.modules.dashboard.service import DashboardService


@strawberry.type
class DashboardSummary:
    total_monitored_directories: int
    total_monitored_files: int
    modified_files_today: int
    added_files_today: int
    deleted_files_today: int
    total_log_events: int
    failed_login_attempts: int
    successful_login_attempts: int
    active_threats: int
    critical_alerts: int
    last_successful_scan: datetime | None = None


@strawberry.type
class DashboardQueries:
    @strawberry.field
    def dashboard_summary(self, info: Info) -> DashboardSummary:
        summary = DashboardService(info.context.db).summary()
        return DashboardSummary(**summary)
