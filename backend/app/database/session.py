from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings


def get_database_url(settings: Settings) -> str | URL:
    if settings.database_url:
        return settings.database_url
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return URL.create(
        "sqlite",
        database=str(settings.storage_dir / "platform.db"),
    )


def create_database_engine(settings: Settings) -> Engine:
    database_url = get_database_url(settings)
    connect_args = {"check_same_thread": False} if str(database_url).startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
