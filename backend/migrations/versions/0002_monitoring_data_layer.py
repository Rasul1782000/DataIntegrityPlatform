"""monitoring data layer: fim, logs, threats, alerts, audit, reports

Revision ID: 0002_monitoring_data_layer
Revises: 0001_auth_foundation
Create Date: 2026-11-16

Creates the monitoring tables (file integrity, log monitoring, threat
detection, alerts, audit trail, reports) and adds the users columns that
were introduced with the model after the initial migration.

Every operation is guarded by an existence check so the migration is safe
to run on partially migrated databases (e.g. SQLite where DDL changes are
hard to roll back atomically).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.database.base import Base
import app.modules.alerts.models  # noqa: F401
import app.modules.audit.models  # noqa: F401
import app.modules.integrity.models  # noqa: F401
import app.modules.log_monitoring.models  # noqa: F401
import app.modules.reports.models  # noqa: F401
import app.modules.threat_detection.models  # noqa: F401

revision: str = "0002_monitoring_data_layer"
down_revision: Union[str, None] = "0001_auth_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_TABLES = (
    "monitored_directories",
    "scan_runs",
    "file_baselines",
    "file_integrity_events",
    "log_sources",
    "security_events",
    "detection_rules",
    "threats",
    "threat_events",
    "alerts",
    "alert_history",
    "audit_logs",
    "reports",
)

NEW_USER_COLUMNS: dict[str, sa.Column] = {
    "full_name": sa.Column("full_name", sa.String(length=128), nullable=True),
    "last_login": sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    "mfa_enabled": sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    "mfa_secret": sa.Column("mfa_secret", sa.String(length=64), nullable=True),
    "mfa_verified": sa.Column("mfa_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    "devices": sa.Column("devices", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    missing = [
        Base.metadata.tables[name]
        for name in NEW_TABLES
        if name in Base.metadata.tables and name not in existing_tables
    ]
    if missing:
        Base.metadata.create_all(bind=bind, tables=missing)

    if "users" in existing_tables:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        for name, column in NEW_USER_COLUMNS.items():
            if name not in user_columns:
                op.add_column("users", column)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for name in reversed(NEW_TABLES):
        if name in existing_tables:
            op.drop_table(name)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    for name in NEW_USER_COLUMNS:
        if name in user_columns:
            op.drop_column("users", name)
