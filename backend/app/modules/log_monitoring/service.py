"""Log ingestion service.

Implements incremental reading of registered text log sources with a byte
offset cursor, truncation/rotation handling, duplicate prevention and UTC
normalization. A Windows Event Log adapter is provided through pywin32 and
degrades gracefully when the dependency or privileges are unavailable.
"""

import hashlib
import ipaddress
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import utc_now_naive
from app.modules.log_monitoring.models import LogSource, SecurityEvent

logger = logging.getLogger(__name__)

MAX_LINE_LENGTH = 64 * 1024  # skip oversized records rather than store them


@dataclass(frozen=True)
class ParsedEvent:
    event_category: str
    event_outcome: str
    severity: str
    username: str | None
    source_ip: str | None
    normalized_timestamp: datetime
    event_description: str
    source_event_id: str | None


# --- text log parsing --------------------------------------------------------

_FAILED_PASSWORD = re.compile(r"Failed \S+ for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+)")
_ACCEPTED = re.compile(r"Accepted (?:password|publickey) for (?P<user>\S+) from (?P<ip>\S+)")
_SUDO = re.compile(r"sudo:\s+(?P<user>\S+)\s*:.*COMMAND=(?P<command>.+)")
_AUTH_FAILURE = re.compile(r"authentication failure.*(?:user=(?P<user>\S+))?")
_SYSLOG_TS = re.compile(r"^(?P<month>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})")
_ISO_TS = re.compile(r"^(?P<iso>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})")

_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _normalize_ip(raw: str | None) -> str | None:
    if not raw or raw.count(".") > 5:
        return None
    candidate = raw.strip("[]()").rstrip(":")
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def _parse_timestamp(line: str) -> datetime:
    match = _ISO_TS.match(line)
    if match:
        try:
            parsed = datetime.fromisoformat(match.group("iso").replace(" ", "T"))
            return parsed if parsed.tzinfo is None else parsed.astimezone(UTC).replace(tzinfo=None)
        except ValueError:
            pass
    match = _SYSLOG_TS.match(line)
    if match:
        month = _MONTHS.get(match.group("month"))
        if month:
            now = datetime.now(UTC)
            hour, minute, second = (int(part) for part in match.group("time").split(":"))
            try:
                parsed = datetime(now.year, month, int(match.group("day")), hour, minute, second)
                # Syslog omits the year; if the parsed date is in the future it belongs to last year.
                if parsed > now:
                    parsed = parsed.replace(year=now.year - 1)
                return parsed
            except ValueError:
                pass
    return utc_now_naive()


def parse_line(line: str) -> ParsedEvent | None:
    """Parse one text log line into a normalized security event."""
    if not line.strip() or len(line) > MAX_LINE_LENGTH:
        return None
    timestamp = _parse_timestamp(line)

    match = _FAILED_PASSWORD.search(line)
    if match:
        ip = _normalize_ip(match.group("ip"))
        if ip:
            return ParsedEvent(
                event_category="authentication",
                event_outcome="failed",
                severity="medium",
                username=match.group("user"),
                source_ip=ip,
                normalized_timestamp=timestamp,
                event_description=f"Failed authentication for '{match.group('user')}' from {ip}",
                source_event_id=None,
            )

    match = _ACCEPTED.search(line)
    if match:
        ip = _normalize_ip(match.group("ip"))
        if ip:
            return ParsedEvent(
                event_category="authentication",
                event_outcome="success",
                severity="low",
                username=match.group("user"),
                source_ip=ip,
                normalized_timestamp=timestamp,
                event_description=f"Successful authentication for '{match.group('user')}' from {ip}",
                source_event_id=None,
            )

    match = _SUDO.search(line)
    if match:
        return ParsedEvent(
            event_category="privilege-escalation",
            event_outcome="success",
            severity="high",
            username=match.group("user"),
            source_ip=None,
            normalized_timestamp=timestamp,
            event_description=f"Privilege escalation: '{match.group('user')}' ran '{match.group('command').strip()[:200]}'",
            source_event_id=None,
        )

    match = _AUTH_FAILURE.search(line)
    if match:
        return ParsedEvent(
            event_category="authentication",
            event_outcome="failed",
            severity="medium",
            username=match.group("user"),
            source_ip=None,
            normalized_timestamp=timestamp,
            event_description=line.strip()[:500],
            source_event_id=None,
        )

    return None


# --- Windows Event Log adapter ------------------------------------------------

def read_windows_security_events(source: LogSource, max_events: int = 500) -> list[ParsedEvent]:
    """Read recent Windows Security log events (4625 failed logon, 4624 success).

    Requires pywin32 and appropriate OS permissions. Raises on unavailability
    so the caller can mark the source health accordingly.
    """
    import win32evtlog  # noqa: PLC0415 - optional dependency, imported lazily

    parsed: list[ParsedEvent] = []
    handle = win32evtlog.OpenEventLog(source.source_path or "Security", "Security")
    try:
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(handle, flags, 0)
        for event in events[:max_events]:
            record_id = getattr(event, "RecordNumber", None)
            timestamp = getattr(event, "TimeGenerated", None)
            if timestamp is not None:
                normalized = timestamp.replace(tzinfo=None) if timestamp.tzinfo is None else timestamp.astimezone(UTC).replace(tzinfo=None)
            else:
                normalized = utc_now_naive()
            raw_event_id = getattr(event, "EventID", None)
            if raw_event_id is None:
                continue
            try:
                eid = int(raw_event_id) & 0xFFFF  # EventID may carry provider high bits
            except (TypeError, ValueError):
                continue
            if eid == 4625:
                parsed.append(
                    ParsedEvent(
                        event_category="authentication",
                        event_outcome="failed",
                        severity="medium",
                        username=None,
                        source_ip=None,
                        normalized_timestamp=normalized,
                        event_description="Windows Security log: failed logon (event 4625)",
                        source_event_id=str(record_id) if record_id else None,
                    )
                )
            elif eid == 4624:
                parsed.append(
                    ParsedEvent(
                        event_category="authentication",
                        event_outcome="success",
                        severity="low",
                        username=None,
                        source_ip=None,
                        normalized_timestamp=normalized,
                        event_description="Windows Security log: successful logon (event 4624)",
                        source_event_id=str(record_id) if record_id else None,
                    )
                )
    finally:
        win32evtlog.CloseEventLog(handle)
    return parsed


# --- ingestion -----------------------------------------------------------------

class LogMonitoringService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register_source(
        self,
        *,
        source_name: str,
        source_type: str = "FILE",
        source_path: str,
        operating_system: str = "windows",
    ) -> LogSource:
        if not source_name.strip():
            raise ValueError("Log source name is required.")
        if source_type not in {"FILE", "WINDOWS_EVENT_LOG"}:
            raise ValueError(f"Unsupported source type: {source_type}")
        if source_type == "FILE":
            from pathlib import Path

            path = Path(source_path).expanduser().resolve()
            if not path.exists() or not path.is_file():
                raise ValueError(f"Log file does not exist: {path}")
            source_path = str(path)
        source = LogSource(
            source_name=source_name.strip(),
            source_type=source_type,
            source_path=source_path,
            operating_system=operating_system,
        )
        self.session.add(source)
        self.session.commit()
        return source

    def ingest_source(self, source_id: str) -> int:
        """Incrementally read new records from a source. Returns stored count."""
        source = self.session.get(LogSource, source_id)
        if source is None:
            raise ValueError("Log source not found.")
        if not source.monitoring_enabled:
            return 0

        try:
            parsed = self._read_new_records(source)
            stored = self._store_parsed_events(source, parsed)
            source.health_status = "HEALTHY"
            source.last_error = None
        except Exception as error:  # noqa: BLE001 - source errors must not kill ingestion
            logger.warning("Ingestion failed for %s: %s", source.source_name, error)
            source.health_status = "ERROR"
            source.last_error = str(error)[:2000]
            stored = 0
        source.last_read_at = utc_now_naive()
        self.session.commit()
        return stored

    def ingest_all_enabled(self) -> int:
        total = 0
        for source in self.session.scalars(select(LogSource).where(LogSource.monitoring_enabled)).all():
            total += self.ingest_source(source.id)
        return total

    def _read_new_records(self, source: LogSource) -> list[ParsedEvent]:
        if source.source_type == "WINDOWS_EVENT_LOG":
            return read_windows_security_events(source)
        return self._read_text_file(source)

    def _read_text_file(self, source: LogSource) -> list[ParsedEvent]:
        from pathlib import Path

        path = Path(source.source_path)
        file_size = path.stat().st_size
        offset = source.last_offset
        if offset > file_size:
            # Log was truncated or rotated: restart from the beginning.
            offset = 0

        parsed: list[ParsedEvent] = []
        with path.open("rb") as handle:
            handle.seek(offset)
            data = handle.read(8 * 1024 * 1024)
        end = offset + len(data)

        lines = data.split(b"\n")
        remainder = lines.pop()  # last chunk may be an incomplete line
        for raw_line in lines:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
            event = parse_line(line)
            if event is not None:
                parsed.append(event)
        if remainder:
            end = offset + len(data) - len(remainder)
        else:
            end = offset + len(data)

        source.last_offset = end
        return parsed

    def _store_parsed_events(self, source: LogSource, parsed: list[ParsedEvent]) -> int:
        stored = 0
        for event in parsed:
            event_hash = hashlib.sha256(
                f"{source.id}|{event.event_category}|{event.username}|{event.source_ip}|"
                f"{event.normalized_timestamp.isoformat()}|{event.event_description}".encode("utf-8")
            ).hexdigest()
            exists = self.session.scalar(
                select(SecurityEvent.id).where(
                    SecurityEvent.source_id == source.id,
                    SecurityEvent.event_hash == event_hash,
                )
            )
            if exists is not None:
                continue
            try:
                self.session.add(
                    SecurityEvent(
                        source_id=source.id,
                        source_event_id=event.source_event_id,
                        event_category=event.event_category,
                        username=event.username,
                        source_ip=event.source_ip,
                        normalized_timestamp=event.normalized_timestamp,
                        event_description=event.event_description,
                        raw_event_reference=None,
                        event_outcome=event.event_outcome,
                        event_hash=event_hash,
                        severity=event.severity,
                    )
                )
                self.session.flush()
                stored += 1
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()
        return stored
