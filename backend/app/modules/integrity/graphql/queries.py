import strawberry
from graphql import GraphQLError


@strawberry.type
class IntegrityQueries:
    @strawberry.field
    def file_status(self, info: strawberry.Info, file_path: str) -> "IntegrityPayload | None":
        return None


@strawberry.type
class SecurityAuditQueries:
    @strawberry.field
    def alert_detail(self, info: strawberry.Info, alert_id: str) -> "SecurityAuditPayload | None":
        return None