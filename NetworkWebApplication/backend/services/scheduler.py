import logging
import threading
import time
from datetime import datetime
from typing import Optional, Callable, Any, Dict

from ..config import get_config
from ..models import device_repository as repo
from .ping import ping_ip

_logger = logging.getLogger(__name__)


class _BaseScheduler:
    """Abstract base for schedulers used to run periodic jobs in background."""

    def start(self) -> None:
        raise NotImplementedError

    def shutdown(self, wait: bool = True) -> None:
        raise NotImplementedError

    def add_job(self, func: Callable, seconds: int) -> None:
        raise NotImplementedError


class _APSchedulerWrapper(_BaseScheduler):
    """Wrapper around APScheduler BackgroundScheduler, if available."""

    def __init__(self) -> None:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.executors.pool import ThreadPoolExecutor
        from apscheduler.jobstores.memory import MemoryJobStore

        # Use in-memory job store and a small thread pool; jobs are lightweight
        self._scheduler = BackgroundScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": ThreadPoolExecutor(max_workers=5)},
            job_defaults={"coalesce": True, "max_instances": 1},
            timezone="UTC",
        )

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            _logger.info("APScheduler BackgroundScheduler started.")

    def shutdown(self, wait: bool = True) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
            _logger.info("APScheduler BackgroundScheduler shut down.")

    def add_job(self, func: Callable, seconds: int) -> None:
        # Replace existing job with the same id to prevent duplication on app reloads
        self._scheduler.add_job(
            func,
            "interval",
            seconds=max(1, int(seconds)),
            id="periodic_ping_all_devices",
            replace_existing=True,
            next_run_time=None,  # start after first interval
        )
        _logger.info("APScheduler job added: run every %s seconds.", seconds)


class _ThreadLoopScheduler(_BaseScheduler):
    """Lightweight thread-based scheduler fallback if APScheduler is unavailable."""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._interval_seconds: int = 0
        self._func: Optional[Callable] = None

    def _run_loop(self) -> None:
        _logger.info("Fallback scheduler thread started with interval=%ss.", self._interval_seconds)
        while not self._stop_event.is_set():
            try:
                if self._func:
                    self._func()
            except Exception as exc:
                _logger.error("Error in scheduled job (fallback): %s", exc)
            # Sleep in small chunks to respond faster to stop
            total = 0
            while total < self._interval_seconds and not self._stop_event.is_set():
                time.sleep(min(1, self._interval_seconds - total) if self._interval_seconds > 0 else 1)
                total += 1
        _logger.info("Fallback scheduler thread exiting.")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        if not self._func or self._interval_seconds <= 0:
            _logger.warning("Fallback scheduler not started: missing job or invalid interval.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="PingSchedulerThread", daemon=True)
        self._thread.start()

    def shutdown(self, wait: bool = True) -> None:
        self._stop_event.set()
        if wait and self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def add_job(self, func: Callable, seconds: int) -> None:
        self._func = func
        self._interval_seconds = max(1, int(seconds))
        _logger.info("Fallback scheduler job registered for every %s seconds.", self._interval_seconds)


def _select_scheduler() -> _BaseScheduler:
    """Select APScheduler if available, otherwise use the thread-based fallback."""
    try:
        # Attempt to import APScheduler
        import apscheduler  # noqa: F401
        _logger.info("APScheduler available; using BackgroundScheduler.")
        return _APSchedulerWrapper()
    except Exception as exc:
        _logger.warning("APScheduler not available (%s); using fallback thread scheduler.", exc)
        return _ThreadLoopScheduler()


def _ping_all_devices_once(timeout_ms: int) -> None:
    """Perform a single pass ping on all devices and update their status and last_ping."""
    try:
        devices = repo.list_devices(None)
    except Exception as exc:
        _logger.error("Unable to list devices for scheduled ping: %s", exc)
        return

    if not devices:
        _logger.debug("No devices to ping in scheduled job.")
        return

    for d in devices:
        ip = d.get("ip_address")
        dev_id = d.get("id")
        if not ip or not dev_id:
            continue
        try:
            result = ping_ip(ip, timeout_ms=timeout_ms)
            update_fields: Dict[str, Any] = {
                "status": result.get("status", "offline"),
                "last_ping": datetime.utcnow(),
            }
            try:
                repo.update_device(dev_id, update_fields)
            except Exception as update_exc:
                _logger.error("Failed to update device %s after ping: %s", dev_id, update_exc)
        except Exception as ping_exc:
            _logger.info("Ping error for device %s (%s): %s", dev_id, ip, ping_exc)


# Store a reference to the scheduler instance so we can shut it down on teardown
_scheduler_instance: Optional[_BaseScheduler] = None


# PUBLIC_INTERFACE
def init_scheduler() -> None:
    """Initialize and start the background scheduler if enabled via environment variables.

    Behavior:
    - If PING_ENABLED is false, the scheduler is not started.
    - If any required env values are invalid, logs a warning and disables the scheduler.
    - Uses APScheduler BackgroundScheduler if available; otherwise a lightweight thread-loop fallback.
    """
    global _scheduler_instance
    cfg = get_config()

    if not cfg.PING_ENABLED:
        _logger.info("PING_ENABLED=false; background scheduler will not start.")
        return

    interval = int(cfg.PING_INTERVAL_SECONDS or 0)
    timeout_ms = int(cfg.PING_TIMEOUT_MS or 0)
    if interval <= 0:
        _logger.warning("Invalid PING_INTERVAL_SECONDS=%s; disabling scheduler.", cfg.PING_INTERVAL_SECONDS)
        return
    if timeout_ms <= 0:
        _logger.warning("Invalid PING_TIMEOUT_MS=%s; using default 1000ms.", cfg.PING_TIMEOUT_MS)
        timeout_ms = 1000

    sched = _select_scheduler()

    def job():
        _ping_all_devices_once(timeout_ms=timeout_ms)

    try:
        sched.add_job(job, seconds=interval)
        sched.start()
        _scheduler_instance = sched
        _logger.info("Background ping scheduler initialized (interval=%ss, timeout=%sms).", interval, timeout_ms)
    except Exception as exc:
        _logger.error("Failed to initialize/start scheduler: %s", exc)
        try:
            sched.shutdown(wait=False)
        except Exception:
            pass
        _scheduler_instance = None


# PUBLIC_INTERFACE
def shutdown_scheduler() -> None:
    """Gracefully shut down the background scheduler if it is running."""
    global _scheduler_instance
    if _scheduler_instance is not None:
        try:
            _scheduler_instance.shutdown(wait=True)
        except Exception as exc:
            _logger.warning("Error during scheduler shutdown: %s", exc)
        finally:
            _scheduler_instance = None
            _logger.info("Background ping scheduler stopped.")
