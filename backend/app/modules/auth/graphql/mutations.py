import strawberry
from strawberry.types import Info
from graphql import GraphQLError
from app.schema import GraphQLContext
from app.modules.auth.graphql.types import AuthPayload, UserType
from app.modules.auth.service import AuthService
from app.config.settings import Settings


@strawberry.input
class LoginInput:
    username: str
    password: str
    remember_me: bool = False


@strawberry.input
class RefreshInput:
    refresh_token: str


@strawberry.type
class AuthMutations:
    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> AuthPayload:
        try:
            settings: Settings = info.context.settings
            tokens = AuthService(info.context.db, settings).login(
                input.username, 
                input.password, 
                remember_me=input.remember_me
            )
        except AuthenticationError as error:
            raise GraphQLError("Invalid username or password.") from error
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise GraphQLError("Authentication system error. Please try again.")
        return AuthPayload(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            remember_me=tokens.remember_me,
            user=UserType.from_model(tokens.user),
        )

    @strawberry.mutation
    def refresh_session(
        self, 
        info: Info, 
        refresh_token: str
    ) -> AuthPayload:
        try:
            settings: Settings = info.context.settings
            tokens = AuthService(info.context.db, settings).refresh(refresh_token)
        except AuthenticationError as error:
            raise GraphQLError("Invalid or expired refresh token.") from error
        except Exception as e:
            logger.error(f"Refresh error: {e}")
            raise GraphQLError("Authentication system error. Please try again.")
        return AuthPayload(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            remember_me=tokens.remember_me,
            user=UserType.from_model(tokens.user),
        )

    @strawberry.mutation
    def logout(self, info: Info, refresh_token: str) -> bool:
        result = AuthService(info.context.db, info.context.settings).logout(refresh_token)
        return result.get("success", False)

    @strawberry.mutation
    def forgot_password(self, info: Info, username: str) -> bool:
        """Initiate password reset flow for a user."""
        try:
            user = AuthService(info.context.db, info.context.settings).users.get_by_username(username.strip().casefold())
            if user is None:
                # Don't reveal if user exists - always return success
                return True
            # In a real implementation, would send reset email
            # provider.send_password_reset_email(user.email, username)
            return True
        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            return False