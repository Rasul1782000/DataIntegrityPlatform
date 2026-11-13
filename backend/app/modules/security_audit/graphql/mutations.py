import strawberry
from graphql import GraphQLError
from app.schema import GraphQLContext
from datetime import datetime
from pydantic import BaseModel


class SecurityAuditInput(BaseModel):
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