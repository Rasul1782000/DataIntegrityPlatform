from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config.logging import configure_logging
from app.config.settings import Settings, get_settings
from app.database.session import create_database_engine, create_session_factory
from app.schema import get_context, schema

from app.modules.auth.service import AuthService

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging()
    engine = create_database_engine(app_settings)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if app_settings.secret_key is None or len(app_settings.secret_key.get_secret_value()) < 32:
            raise RuntimeError("APP_SECRET_KEY must contain at least 32 characters.")
        if app_settings.is_production and app_settings.bootstrap_admin_password is not None:
            logger.warning(
                "Bootstrap credentials are configured in production; remove them after first startup."
            )
        # Bootstrap admin creation is not yet implemented - skip for now
        # TODO: Implement AuthService.create_bootstrap_admin() when user management is added
        yield
        engine.dispose()

    application = FastAPI(
        title="Data Integrity & Security Monitoring Platform",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.state.settings = app_settings
    application.state.engine = engine
    application.state.session_factory = session_factory

    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(
        GraphQLRouter(
            schema,
            context_getter=get_context,
            graphql_ide=None if app_settings.is_production else "graphiql",
        ),
        prefix="/graphql",
    )

    @application.get("/health/live", include_in_schema=False)
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready", include_in_schema=False)
    def readiness() -> dict[str, str]:
        try:
            with session_factory() as session:
                session.execute(text("SELECT 1"))
        except Exception as error:
            logger.exception("Database readiness check failed.")
            raise HTTPException(status_code=503, detail="Database is unavailable.") from error
        return {"status": "ready"}

    return application


app = create_app()