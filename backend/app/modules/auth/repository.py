from datetime import datetime
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import User, RefreshSession


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: str) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(func.lower(User.username) == username.casefold())
        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.casefold())
        return self.session.scalar(statement)

    def has_users(self) -> bool:
        return self.session.scalar(select(User.id).limit(1)) is not None

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def list_users(self, limit: int = 100) -> list[User]:
        statement = select(User).order_by(User.created_at.desc()).limit(max(1, min(limit, 500)))
        return list(self.session.scalars(statement).all())


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_refresh_session(self, token_hash: str) -> RefreshSession | None:
        statement = select(RefreshSession).where(RefreshSession.token_hash == token_hash)
        return self.session.scalar(statement)

    def revoke_if_active(self, session_id: str, now: datetime) -> bool:
        statement = (
            update(RefreshSession)
            .where(
                RefreshSession.id == session_id,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > now,
            )
            .values(revoked_at=now)
        )
        result = self.session.execute(statement)
        return result.rowcount == 1

    def add_refresh_session(self, refresh_session: RefreshSession) -> None:
        self.session.add(refresh_session)