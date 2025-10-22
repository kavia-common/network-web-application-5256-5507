import logging
from datetime import datetime
from typing import Dict

from pythonping import ping

_logger = logging.getLogger(__name__)


# PUBLIC_INTERFACE
def ping_ip(ip_address: str, timeout_ms: int) -> Dict[str, object]:
    """Ping an IP address and return status, latency, and timestamp.

    Args:
        ip_address: Target IPv4 address to ping.
        timeout_ms: Timeout per ping in milliseconds.

    Returns:
        dict: {
            "status": "online" | "offline",
            "latency_ms": float | None,
            "timestamp": ISO 8601 string
        }

    Notes:
        - Uses one ICMP echo request for a quick check.
        - Exceptions are caught and reported as offline.
    """
    now = datetime.utcnow().isoformat() + "Z"
    try:
        # pythonping timeout parameter is in seconds
        timeout_sec = max(1, int(round(timeout_ms / 1000.0))) if timeout_ms else 1
        result = ping(ip_address, count=1, timeout=timeout_sec, privileged=False)

        # result.success() True if any response received
        if result.success():
            # Average RTT is in seconds; convert to ms (use first/avg safely)
            try:
                rtt_s = result.rtt_avg
                latency_ms = round(float(rtt_s) * 1000.0, 3) if rtt_s is not None else None
            except Exception:
                latency_ms = None
            return {"status": "online", "latency_ms": latency_ms, "timestamp": now}
        else:
            return {"status": "offline", "latency_ms": None, "timestamp": now}
    except Exception as exc:
        _logger.info("Ping error for %s: %s", ip_address, exc)
        return {"status": "offline", "latency_ms": None, "timestamp": now}
