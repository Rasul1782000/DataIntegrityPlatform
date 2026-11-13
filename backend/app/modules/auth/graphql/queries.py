import strawberry
from strawberry.types import Info
from graphql import GraphQLError
from app.schema import GraphQLContext
from app.modules.auth.graphql.types import UserType


@strawberry.type
class AuthQueries:
    @strawberry.field
    def me(self, info: Info) -> UserType | None:
        user = info.context.current_user
        if user is None:
            return None
        return UserType.from_model(user)

    @strawberry.field
    def account_status(self, info: Info) -> dict:
        """Check account lock status and details."""
        from app.modules.auth.service import AuthService
        from app.config.settings import Settings
        
        settings: Settings = info.context.settings
        user = info.context.current_user
        if user is None:
            return {"locked": False, "error": "not_authenticated"}
        
        # Use the service to check lock status
        service = AuthService(info.context.db, settings)
        return service.is_account_locked(user.id)