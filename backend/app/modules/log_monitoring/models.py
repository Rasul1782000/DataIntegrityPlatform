import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import utc_now_naive
from app.database.base import Base


class LogSource(Base):
    __tablename__ = "log_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), default="FILE", nullable=False)  # FILE/WINDOWS_EVENT_LOG
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    operating_system: Mapped[str] = mapped_column(String(16), default="windows", nullable=False)
    monitoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    health_status: Mapped[str] = mapped_column(String(16), default="HEALTHY", nullable=False)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_offset: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    __table_args__ = (
        Index("uq_security_events_source_hash", "source_id", "event_hash", unique=True),
        Index("ix_security_events_timestamp", "normalized_timestamp"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("log_sources.id"), index=True, nullable=False)
    source_event_id: Mapped[str | None] = mapped_column(String(64))
    event_category: Mapped[str] = mapped_column(String(32), default="other", nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45), index=True)
    normalized_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_description: Mapped[str] = mapped_column(Text, nullable=False)
    raw_event_reference: Mapped[str | None] = mapped_column(Text)
    event_outcome: Mapped[str] = mapped_column(String(16), default="unknown", nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="low", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)
