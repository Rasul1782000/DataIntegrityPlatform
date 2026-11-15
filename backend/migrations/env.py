from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config.settings import get_settings
from app.database.base import Base
from app.database.session import create_database_engine, get_database_url
import app.modules.auth.models  # noqa: F401
import app.modules.alerts.models  # noqa: F401
import app.modules.audit.models  # noqa: F401
import app.modules.integrity.models  # noqa: F401
import app.modules.log_monitoring.models  # noqa: F401
import app.modules.reports.models  # noqa: F401
import app.modules.threat_detection.models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    settings = get_settings()
    context.configure(
        url=str(get_database_url(settings)),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    settings = get_settings()
    connectable = create_database_engine(settings)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
