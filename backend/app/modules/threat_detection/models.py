import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import utc_now_naive
from app.database.base import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(String(48), nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    time_window_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="high", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive
    )


class Threat(Base):
    __tablename__ = "threats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_type: Mapped[str] = mapped_column(String(48), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="high", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    source_ip: Mapped[str | None] = mapped_column(String(45), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    related_event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    detection_rule_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("detection_rules.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)


class ThreatEvent(Base):
    __tablename__ = "threat_events"
    __table_args__ = (
        UniqueConstraint("threat_id", "security_event_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_id: Mapped[str] = mapped_column(String(36), ForeignKey("threats.id"), index=True, nullable=False)
    security_event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("security_events.id"), index=True, nullable=False
    )
