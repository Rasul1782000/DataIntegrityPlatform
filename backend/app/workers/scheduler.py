"""Background monitoring worker.

Runs inside the FastAPI process via APScheduler. Each tick:
1. Incrementally ingests every enabled log source and evaluates detection
   rules over the newly stored events.
2. Starts a scheduled scan for every enabled directory whose scan frequency
   is due (never for MANUAL directories).

The tick is guarded by a lock so overlapping runs are impossible, and every
session is short-lived so SQLite stays healthy.
"""

import logging
import threading
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.security import utc_now_naive
from app.modules.integrity.models import MonitoredDirectory, ScanRun
from app.modules.integrity.repository import IntegrityRepository
from app.modules.integrity.service import IntegrityService
from app.modules.log_monitoring.service import LogMonitoringService
from app.modules.threat_detection.service import ThreatDetectionService

logger = logging.getLogger(__name__)

SCAN_FREQUENCY_SECONDS = {
    "FIVE_MINUTES": 300,
    "FIFTEEN_MINUTES": 900,
    "THIRTY_MINUTES": 1800,
    "HOURLY": 3600,
    "SIX_HOURS": 21600,
    "TWELVE_HOURS": 43200,
    "DAILY": 86400,
}

TICK_SECONDS = 60


class MonitoringScheduler:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory
        self._scheduler = BackgroundScheduler(timezone="UTC")
        self._tick_lock = threading.Lock()

    def start(self) -> None:
        self._scheduler.add_job(
            self._tick,
            trigger="interval",
            seconds=TICK_SECONDS,
            id="monitoring_tick",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        logger.info("Monitoring scheduler started (tick every %ss).", TICK_SECONDS)

    def stop(self) -> None:
        try:
            self._scheduler.shutdown(wait=False)
        except Exception:  # noqa: BLE001 - shutdown must never break the app
            logger.warning("Monitoring scheduler shutdown raised.", exc_info=True)

    # -- tick ------------------------------------------------------------------

    def _tick(self) -> None:
        if not self._tick_lock.acquire(blocking=False):
            return
        try:
            self._ingest_sources()
            self._run_due_scans()
        except Exception:  # noqa: BLE001 - the worker must survive any failure
            logger.exception("Monitoring tick failed.")
        finally:
            self._tick_lock.release()

    def _ingest_sources(self) -> None:
        with self._session_factory() as session:
            stored = LogMonitoringService(session).ingest_all_enabled()
            if stored:
                ThreatDetectionService(session).evaluate_recent_events()
                logger.info("Ingested %s new security event(s).", stored)

    def _run_due_scans(self) -> None:
        with self._session_factory() as session:
            repo = IntegrityRepository(session)
            now = utc_now_naive()
            for directory in list(
                session.query(MonitoredDirectory).filter(MonitoredDirectory.monitoring_enabled).all()
            ):
                frequency = SCAN_FREQUENCY_SECONDS.get(directory.scan_frequency)
                if frequency is None:  # MANUAL
                    continue
                if repo.get_running_scan(directory.id) is not None:
                    continue  # overlap prevention
                last = repo.last_completed_scan_for_directory(directory.id)
                if last is not None and last.completed_at and last.completed_at > now - timedelta(seconds=frequency):
                    continue
                session.expire_all()
                try:
                    IntegrityService(session).start_scan(directory.id, initiated_by="scheduler", trigger="SCHEDULED")
                except Exception:  # noqa: BLE001
                    logger.warning("Scheduled scan for %s could not start.", directory.name, exc_info=True)
