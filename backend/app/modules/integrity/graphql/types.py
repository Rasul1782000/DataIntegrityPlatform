from datetime import datetime

import strawberry

from app.modules.integrity.models import FileIntegrityEvent, MonitoredDirectory, ScanRun


@strawberry.type
class MonitoredDirectoryType:
    id: strawberry.ID
    name: str
    canonical_path: str
    description: str | None = None
    monitoring_enabled: bool = True
    scan_frequency: str = "MANUAL"
    recursive: bool = True
    created_at: datetime | None = None

    @classmethod
    def from_model(cls, model: MonitoredDirectory) -> "MonitoredDirectoryType":
        return cls(
            id=strawberry.ID(model.id),
            name=model.name,
            canonical_path=model.canonical_path,
            description=model.description,
            monitoring_enabled=model.monitoring_enabled,
            scan_frequency=model.scan_frequency,
            recursive=model.recursive,
            created_at=model.created_at,
        )


@strawberry.type
class ScanRunType:
    id: strawberry.ID
    directory_id: strawberry.ID
    status: str
    trigger: str
    started_at: datetime
    completed_at: datetime | None = None
    files_examined: int = 0
    errors_count: int = 0
    error_summary: str | None = None

    @classmethod
    def from_model(cls, model: ScanRun) -> "ScanRunType":
        return cls(
            id=strawberry.ID(model.id),
            directory_id=strawberry.ID(model.directory_id),
            status=model.status,
            trigger=model.trigger,
            started_at=model.started_at,
            completed_at=model.completed_at,
            files_examined=model.files_examined,
            errors_count=model.errors_count,
            error_summary=model.error_summary,
        )


@strawberry.type
class FileIntegrityEventType:
    id: strawberry.ID
    directory_id: strawberry.ID
    directory_name: str
    relative_path: str
    event_type: str
    previous_hash: str | None = None
    current_hash: str | None = None
    file_size: int | None = None
    severity: str
    status: str
    detected_at: datetime

    @classmethod
    def from_model(cls, model: FileIntegrityEvent, directory_name: str) -> "FileIntegrityEventType":
        return cls(
            id=strawberry.ID(model.id),
            directory_id=strawberry.ID(model.directory_id),
            directory_name=directory_name,
            relative_path=model.relative_path,
            event_type=model.event_type,
            previous_hash=model.previous_hash,
            current_hash=model.current_hash,
            file_size=model.file_size,
            severity=model.severity,
            status=model.status,
            detected_at=model.detected_at,
        )


@strawberry.type
class FileBaselinesAggregate:
    count: int


@strawberry.input
class RegisterDirectoryInput:
    name: str
    path: str
    description: str | None = None
    recursive: bool = True
    scan_frequency: str = "MANUAL"
    included_extensions: list[str] | None = None
    excluded_extensions: list[str] | None = None
    excluded_subdirectories: list[str] | None = None
    max_file_size: int | None = None
