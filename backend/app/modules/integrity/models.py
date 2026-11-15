import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import utc_now_naive
from app.database.base import Base


class MonitoredDirectory(Base):
    __tablename__ = "monitored_directories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    canonical_path: Mapped[str] = mapped_column(String(1024), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    recursive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    monitoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scan_frequency: Mapped[str] = mapped_column(String(32), default="MANUAL", nullable=False)
    included_extensions: Mapped[str | None] = mapped_column(Text)  # JSON list, None = all
    excluded_extensions: Mapped[str | None] = mapped_column(Text)  # JSON list
    excluded_subdirectories: Mapped[str | None] = mapped_column(Text)  # JSON list
    max_file_size: Mapped[int | None] = mapped_column(BigInteger)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now_naive, onupdate=utc_now_naive
    )

    scans: Mapped[list["ScanRun"]] = relationship(back_populates="directory")


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    directory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("monitored_directories.id"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), default="RUNNING", nullable=False)  # RUNNING/COMPLETED/FAILED
    trigger: Mapped[str] = mapped_column(String(16), default="MANUAL", nullable=False)  # MANUAL/SCHEDULED/INITIAL
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    files_examined: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    initiated_by: Mapped[str | None] = mapped_column(String(64))
    error_summary: Mapped[str | None] = mapped_column(Text)

    directory: Mapped[MonitoredDirectory] = relationship(back_populates="scans")


class FileBaseline(Base):
    __tablename__ = "file_baselines"
    __table_args__ = (
        Index("uq_baseline_dir_path_version", "directory_id", "relative_path", "baseline_version", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    directory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("monitored_directories.id"), index=True, nullable=False
    )
    relative_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    baseline_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    scan_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)


class FileIntegrityEvent(Base):
    __tablename__ = "file_integrity_events"
    __table_args__ = (Index("ix_fie_detected_at", "detected_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    directory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("monitored_directories.id"), index=True, nullable=False
    )
    scan_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    relative_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    event_type: Mapped[str] = mapped_column(String(24), nullable=False)
    previous_hash: Mapped[str | None] = mapped_column(String(64))
    current_hash: Mapped[str | None] = mapped_column(String(64))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now_naive)
