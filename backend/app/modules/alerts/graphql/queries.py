import strawberry
from strawberry.types import Info

from app.modules.alerts.graphql.types import AlertType
from app.modules.alerts.service import AlertsService


@strawberry.type
class AlertQueries:
    @strawberry.field
    def alerts(self, info: Info, order_by: str | None = "createdAt_DESC", limit: int = 50) -> list[AlertType]:
        alerts = AlertsService(info.context.db).list_alerts(order_by=order_by, limit=limit)
        return [AlertType.from_model(alert) for alert in alerts]
