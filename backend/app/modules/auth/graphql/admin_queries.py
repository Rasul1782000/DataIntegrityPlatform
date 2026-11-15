import strawberry
from datetime import datetime
from strawberry.types import Info

from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository


@strawberry.type
class UserAccountType:
    id: strawberry.ID
    username: str
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime | None = None


@strawberry.type
class UserManagementQueries:
    @strawberry.field
    def users(self, info: Info, order_by: str | None = "createdAt_DESC", limit: int = 100) -> list[UserAccountType]:
        del order_by  # repository orders by created_at desc
        users = UserRepository(info.context.db).list_users(limit=limit)
        return [
            UserAccountType(
                id=strawberry.ID(user.id),
                username=user.username,
                email=user.email,
                full_name=getattr(user, "full_name", None),
                role=user.role.value if hasattr(user.role, "value") else str(user.role),
                is_active=user.is_active,
                last_login=user.last_login,
                created_at=user.created_at,
            )
            for user in users
        ]
