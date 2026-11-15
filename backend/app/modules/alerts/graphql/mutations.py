import strawberry
from strawberry.types import Info

from app.modules.alerts.graphql.types import AlertType
from app.modules.alerts.service import AlertsService


@strawberry.type
class AlertMutationPayload:
    alert: AlertType | None = None
    error: str | None = None


@strawberry.type
class AlertMutations:
    @strawberry.mutation
    def acknowledge_alert(self, info: Info, alert_id: strawberry.ID, note: str | None = None) -> AlertMutationPayload:
        alert = AlertsService(info.context.db).transition(
            str(alert_id), action="acknowledged", new_status="acknowledged", note=note
        )
        if alert is None:
            return AlertMutationPayload(error="Alert not found.")
        return AlertMutationPayload(alert=AlertType.from_model(alert))

    @strawberry.mutation
    def resolve_alert(self, info: Info, alert_id: strawberry.ID, note: str | None = None) -> AlertMutationPayload:
        alert = AlertsService(info.context.db).transition(
            str(alert_id), action="resolved", new_status="resolved", note=note
        )
        if alert is None:
            return AlertMutationPayload(error="Alert not found.")
        return AlertMutationPayload(alert=AlertType.from_model(alert))

    @strawberry.mutation
    def assign_alert(self, info: Info, alert_id: strawberry.ID, assigned_to: str) -> AlertMutationPayload:
        alert = AlertsService(info.context.db).transition(
            str(alert_id), action="assigned", new_status="investigating", assigned_to=assigned_to
        )
        if alert is None:
            return AlertMutationPayload(error="Alert not found.")
        return AlertMutationPayload(alert=AlertType.from_model(alert))
