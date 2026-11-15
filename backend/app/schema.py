from dataclasses import dataclass
from collections.abc import Iterator

import strawberry
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext
from strawberry.types import Info
from typing import Any

from app.config.settings import Settings
from app.modules.auth.graphql.types import UserType, AuthPayload
from app.modules.auth.service import AuthService
from app.modules.auth.models import User

from app.modules.auth.graphql.admin_queries import UserManagementQueries
from app.modules.dashboard.graphql import DashboardQueries
from app.modules.integrity.graphql.queries import IntegrityQueries
from app.modules.integrity.graphql.mutations import IntegrityMutations
from app.modules.log_monitoring.graphql.queries import LogMonitoringQueries
from app.modules.log_monitoring.graphql.mutations import LogMonitoringMutations
from app.modules.threat_detection.graphql.queries import ThreatDetectionQueries
from app.modules.alerts.graphql.queries import AlertQueries
from app.modules.alerts.graphql.mutations import AlertMutations
from app.modules.audit.graphql.queries import AuditQueries
from app.modules.reports.graphql.queries import ReportQueries
from app.modules.reports.graphql.mutations import ReportMutations


# ---------------------------------------------------------------------------
# GraphQL request context
# ---------------------------------------------------------------------------


@dataclass
class GraphQLContext(BaseContext):
    db: Session
    settings: Settings
    current_user: User | None
    service: AuthService = None

    def require_user(self) -> User:
        if self.current_user is None:
            raise ValueError("Authentication is required.")
        return self.current_user


def get_db(request: Request) -> Iterator[Session]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


def get_context(
    request: Request,
    db: Session = Depends(get_db),
) -> GraphQLContext:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.casefold() != "bearer" or not token.strip():
        token = ""
    settings: Settings = request.app.state.settings
    service = AuthService(db, settings)
    current_user = service.authenticate_access_token(token.strip() or None)
    return GraphQLContext(db=db, settings=settings, current_user=current_user, service=service)


# ---------------------------------------------------------------------------
# GraphQL schema (composed from feature modules)
# ---------------------------------------------------------------------------


@strawberry.input
class LoginInput:
    username: str
    password: str
    rememberMe: bool = False
    mfaCode: str | None = None


@strawberry.type
class Query(
    UserManagementQueries,
    DashboardQueries,
    IntegrityQueries,
    LogMonitoringQueries,
    ThreatDetectionQueries,
    AlertQueries,
    AuditQueries,
    ReportQueries,
):
    @strawberry.field
    def me(self, info: Info) -> UserType | None:
        """Get current authenticated user."""
        context = info.context
        if hasattr(context, "current_user") and context.current_user is not None:
            return UserType.from_model(context.current_user)
        return None


@strawberry.type
class Mutation(IntegrityMutations, LogMonitoringMutations, AlertMutations, ReportMutations):
    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> AuthPayload:
        """Login user and return auth tokens."""
        service: AuthService = info.context.service
        tokens = service.login(
            input.username,
            input.password,
            remember_me=input.rememberMe,
            mfa_code=input.mfaCode,
        )
        return AuthPayload(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user=UserType.from_model(tokens.user),
            rememberMe=tokens.remember_me,
            mfaVerified=tokens.mfa_verified,
        )

    @strawberry.mutation
    def refreshSession(self, info: Info, refresh_token: str) -> AuthPayload:
        """Refresh session and return new tokens."""
        service: AuthService = info.context.service
        tokens = service.refresh(refresh_token)
        return AuthPayload(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user=UserType.from_model(tokens.user),
            rememberMe=tokens.remember_me,
            mfaVerified=tokens.mfa_verified,
        )

    @strawberry.mutation
    def logout(self, info: Info, refresh_token: str) -> bool:
        """Logout and revoke refresh token."""
        service: AuthService = info.context.service
        result = service.logout(refresh_token)
        return result.get("success", False)


schema = strawberry.Schema(query=Query, mutation=Mutation)
