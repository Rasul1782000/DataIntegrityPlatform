from datetime import datetime

import strawberry
from app.core.permissions import UserRole
from app.modules.auth.models import User


@strawberry.type
class UserType:
    id: strawberry.ID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None
    is_locked: bool = False
    is_mfa_enabled: bool = False

    @classmethod
    def from_model(cls, user: User) -> "UserType":
        role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        is_locked = user.locked_until is not None and user.locked_until > datetime.now(UTC).replace(tzinfo=None)
        return cls(
            id=strawberry.ID(user.id),
            username=user.username,
            email=user.email,
            role=role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            is_locked=is_locked,
            is_mfa_enabled=user.mfa_enabled,
        )


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserType
    rememberMe: bool = False
    mfaVerified: bool = False