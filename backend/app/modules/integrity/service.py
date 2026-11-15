"""File integrity monitoring service.

Implements real SHA-256 hashing (chunked reads so large files never load
fully into memory), trusted baseline creation and change detection against
the latest baseline version. Scan state is persisted so results survive
process restarts and overlapping scans are refused.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PureWindowsPath

from sqlalchemy.orm import Session

from app.core.security import utc_now_naive
from app.modules.integrity.models import FileBaseline, FileIntegrityEvent, MonitoredDirectory, ScanRun
from app.modules.integrity.repository import IntegrityRepository

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024  # 1 MiB

ALLOWED_SCAN_FREQUENCIES = {
    "MANUAL",
    "FIVE_MINUTES",
    "FIFTEEN_MINUTES",
    "THIRTY_MINUTES",
    "HOURLY",
    "SIX_HOURS",
    "TWELVE_HOURS",
    "DAILY",
}

SEVERITY_BY_EVENT_TYPE = {
    "CREATED": "medium",
    "MODIFIED": "high",
    "DELETED": "high",
    "MOVED": "high",
    "PERMISSION_CHANGED": "medium",
    "SCAN_ERROR": "medium",
}


@dataclass(frozen=True)
class DirectoryValidationError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.message


def compute_sha256(file_path: Path) -> str:
    """Stream a file in 1 MiB chunks and return its SHA-256 hex digest."""
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonicalize_path(raw_path: str) -> Path:
    """Resolve and canonicalize a directory path without following symlinks."""
    candidate = Path(PureWindowsPath(raw_path)) if "\\" in raw_path else Path(raw_path)
    return candidate.expanduser().resolve()


def validate_directory_path(canonical: Path) -> None:
    if not canonical.exists():
        raise DirectoryValidationError(f"Path does not exist: {canonical}")
    if not canonical.is_dir():
        raise DirectoryValidationError(f"Path is not a directory: {canonical}")


class IntegrityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = IntegrityRepository(session)

    # -- directory management ------------------------------------------------

    def register_directory(
        self,
        *,
        name: str,
        path: str,
        description: str | None = None,
        recursive: bool = True,
        scan_frequency: str = "MANUAL",
        included_extensions: list[str] | None = None,
        excluded_extensions: list[str] | None = None,
        excluded_subdirectories: list[str] | None = None,
        max_file_size: int | None = None,
        created_by: str | None = None,
    ) -> MonitoredDirectory:
        if not name.strip():
            raise DirectoryValidationError("Directory name is required.")
        if scan_frequency not in ALLOWED_SCAN_FREQUENCIES:
            raise DirectoryValidationError(f"Unsupported scan frequency: {scan_frequency}")
        if max_file_size is not None and max_file_size <= 0:
            raise DirectoryValidationError("Maximum file size must be positive.")

        canonical = canonicalize_path(path)
        validate_directory_path(canonical)
        if self.repo.get_directory_by_path(str(canonical)) is not None:
            raise DirectoryValidationError("This path is already being monitored.")

        directory = MonitoredDirectory(
            name=name.strip(),
            canonical_path=str(canonical),
            description=description,
            recursive=recursive,
            scan_frequency=scan_frequency,
            included_extensions=self._encode_list(included_extensions),
            excluded_extensions=self._encode_list(excluded_extensions),
            excluded_subdirectories=self._encode_list(excluded_subdirectories),
            max_file_size=max_file_size,
            created_by=created_by,
        )
        directory = self.repo.add_directory(directory)
        self.session.commit()
        return directory

    @staticmethod
    def _encode_list(values: list[str] | None) -> str | None:
        if not values:
            return None
        cleaned = sorted({value.strip().lstrip(".").casefold() for value in values if value.strip()})
        return json.dumps(cleaned) if cleaned else None

    @staticmethod
    def _decode_list(raw: str | None) -> list[str]:
        if not raw:
            return []
        try:
            return list(json.loads(raw))
        except (json.JSONDecodeError, TypeError):
            return []

    # -- scanning ------------------------------------------------------------

    def start_scan(self, directory_id: str, *, initiated_by: str | None = None, trigger: str = "MANUAL") -> ScanRun:
        directory = self.repo.get_directory(directory_id)
        if directory is None:
            raise DirectoryValidationError("Monitored directory not found.")
        if not directory.monitoring_enabled:
            raise DirectoryValidationError("Monitoring is paused for this directory.")
        existing = self.repo.get_running_scan(directory_id)
        if existing is not None:
            raise DirectoryValidationError("A scan is already running for this directory.")

        scan = self.repo.add_scan(
            ScanRun(directory_id=directory_id, status="RUNNING", trigger=trigger, initiated_by=initiated_by)
        )
        self.session.commit()

        try:
            self._execute_scan(directory, scan)
        except Exception as error:  # noqa: BLE001 - scan must never crash the API
            logger.exception("Scan %s failed.", scan.id)
            scan.status = "FAILED"
            scan.completed_at = utc_now_naive()
            scan.error_summary = str(error)
            self.session.commit()
        return scan

    def _execute_scan(self, directory: MonitoredDirectory, scan: ScanRun) -> None:
        root = Path(directory.canonical_path)
        current_state: dict[str, tuple[str, int, datetime | None]] = {}
        scan_errors = 0

        for file_path, relative_path in self._iter_candidate_files(directory):
            try:
                digest = compute_sha256(file_path)
                size = file_path.stat().st_size
                modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
                current_state[relative_path] = (digest, size, modified_at)
            except (OSError, PermissionError) as error:
                scan_errors += 1
                self.repo.add_events(
                    [
                        FileIntegrityEvent(
                            directory_id=directory.id,
                            scan_id=scan.id,
                            relative_path=relative_path,
                            event_type="SCAN_ERROR",
                            severity=SEVERITY_BY_EVENT_TYPE["SCAN_ERROR"],
                            detected_at=utc_now_naive(),
                        )
                    ]
                )
                logger.warning("Could not hash %s: %s", file_path, error)

        baseline_entries = {entry.relative_path: entry for entry in self.repo.baseline_entries(directory.id)}
        new_events: list[FileIntegrityEvent] = []

        if not baseline_entries:
            # Initial trusted baseline: no events, version 1.
            self.repo.add_baseline_entries(
                [
                    FileBaseline(
                        directory_id=directory.id,
                        relative_path=relative_path,
                        sha256_hash=digest,
                        file_size=size,
                        modified_at=modified_at,
                        baseline_version=1,
                        scan_id=scan.id,
                    )
                    for relative_path, (digest, size, modified_at) in sorted(current_state.items())
                ]
            )
        else:
            baseline_paths = set(baseline_entries)
            current_paths = set(current_state)

            for path in current_paths - baseline_paths:
                digest, size, _ = current_state[path]
                new_events.append(
                    self._make_event(directory.id, scan.id, path, "CREATED", None, digest, size)
                )
            for path in current_paths & baseline_paths:
                entry = baseline_entries[path]
                digest, size, _ = current_state[path]
                if entry.sha256_hash != digest:
                    new_events.append(
                        self._make_event(
                            directory.id, scan.id, path, "MODIFIED", entry.sha256_hash, digest, size
                        )
                    )
            for path in baseline_paths - current_paths:
                entry = baseline_entries[path]
                new_events.append(
                    self._make_event(directory.id, scan.id, path, "DELETED", entry.sha256_hash, None, None)
                )

            self.repo.add_events(new_events)

        scan.status = "COMPLETED"
        scan.completed_at = utc_now_naive()
        scan.files_examined = len(current_state) + scan_errors
        scan.errors_count = scan_errors
        self.session.commit()
        logger.info(
            "Scan %s for %s completed: %s files, %s events, %s errors.",
            scan.id,
            directory.name,
            scan.files_examined,
            len(new_events),
            scan_errors,
        )

    def _make_event(
        self,
        directory_id: str,
        scan_id: str,
        relative_path: str,
        event_type: str,
        previous_hash: str | None,
        current_hash: str | None,
        file_size: int | None,
    ) -> FileIntegrityEvent:
        return FileIntegrityEvent(
            directory_id=directory_id,
            scan_id=scan_id,
            relative_path=relative_path,
            event_type=event_type,
            previous_hash=previous_hash,
            current_hash=current_hash,
            file_size=file_size,
            severity=SEVERITY_BY_EVENT_TYPE.get(event_type, "medium"),
            detected_at=utc_now_naive(),
        )

    def _iter_candidate_files(self, directory: MonitoredDirectory):
        root = Path(directory.canonical_path)
        included = set(self._decode_list(directory.included_extensions))
        excluded = set(self._decode_list(directory.excluded_extensions))
        excluded_subdirs = set(self._decode_list(directory.excluded_subdirectories))

        iterator = root.rglob("*") if directory.recursive else root.iterdir()
        for file_path in iterator:
            try:
                if not file_path.is_file() or file_path.is_symlink():
                    continue
                relative_path = file_path.relative_to(root).as_posix()
                parent_parts = relative_path.split("/")[:-1]
                if any(part in excluded_subdirs for part in parent_parts):
                    continue
                extension = file_path.suffix.casefold()
                if included and extension not in included:
                    continue
                if extension in excluded:
                    continue
                if directory.max_file_size is not None and file_path.stat().st_size > directory.max_file_size:
                    continue
            except OSError:
                continue
            yield file_path, relative_path

    # -- reads exposed to GraphQL ---------------------------------------------

    def recent_events(self, limit: int) -> list[tuple[FileIntegrityEvent, str]]:
        return self.repo.recent_events(limit)

    def dashboard_counts(self) -> dict[str, int | datetime | None]:
        return {
            "total_monitored_directories": self.repo.count_enabled_directories(),
            "total_monitored_files": self.repo.baseline_count(),
            "modified_files_today": self.repo.count_events_today("MODIFIED"),
            "added_files_today": self.repo.count_events_today("CREATED"),
            "deleted_files_today": self.repo.count_events_today("DELETED"),
            "last_successful_scan": (
                self.repo.last_completed_scan().completed_at if self.repo.last_completed_scan() else None
            ),
        }
