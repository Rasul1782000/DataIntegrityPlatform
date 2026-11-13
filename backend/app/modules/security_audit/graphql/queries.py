from typing import Any
import strawberry
from graphql import GraphQLError


@strawberry.type
class SecurityAuditQueries:
    @strawberry.field
    def alert_detail(
        self, info: strawberry.Info[Any, None], alert_id: str
    ) -> "SecurityAuditPayload | None":
        return None