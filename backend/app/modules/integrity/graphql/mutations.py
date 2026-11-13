import strawberry
from graphql import GraphQLError
from app.schema import GraphQLContext
from datetime import datetime


@strawberry.input
class IntegrityInput:
    file_path: str
    event_type: str
    directory_name: str
    severity: str


@strawberry.type
class IntegrityMutations:
    @strawberry.mutation
    def record_integrity_event(
        self,
        info: strawberry.Info[GraphQLContext, None],
        input: IntegrityInput,
    ) -> "IntegrityPayload":
        return IntegrityPayload(
            file_path=input.file_path,
            event_type=input.event_type,
            severity=input.severity,
            checked_at=datetime.now(),
            status="recorded",
        )


@strawberry.input
class SecurityAuditInput:
    alert_title: str
    alert_description: str
    alert_severity: str
    alert_id: str


@strawberry.type
class SecurityAuditMutations:
    @strawberry.mutation
    def create_alert(
        self,
        info: strawberry.Info[GraphQLContext, None],
        input: SecurityAuditInput,
    ) -> "SecurityAuditPayload":
        return SecurityAuditPayload(
            alert_id=input.alert_id,
            title=input.alert_title,
            severity=input.alert_severity,
            described=input.alert_description,
            generated_at=datetime.now(),
        )