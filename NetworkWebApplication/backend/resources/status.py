import logging
from datetime import datetime
from typing import Any, Dict, Optional

from flask import jsonify
from flask_restful import Resource

from ..models import device_repository as repo
from ..services.ping import ping_ip
from ..utils.responses import success, error
from ..config import get_config

_logger = logging.getLogger(__name__)


class DeviceStatusResource(Resource):
    """Resource to manually check a device's online status via ping.

    GET /api/devices/<string:device_id>/status

    - Validates device_id format.
    - Ensures device exists; returns 404 if not found.
    - Uses pythonping (via services.ping.ping_ip) to ping the device's IP.
    - Updates the device's 'status' and 'last_ping' fields in the database.
    - Returns a standardized JSON response with ping details and updated device info.
    """

    # PUBLIC_INTERFACE
    def get(self, device_id: str):
        """Check status of a device by id and update it.

        Path params:
            device_id: string ObjectId hex.

        Returns:
            200 with data:
                {
                  "device": <device dict after update>,
                  "ping": { "status": "online|offline", "latency_ms": <float|null>, "timestamp": <iso> }
                }
            400 for invalid id,
            404 for missing device,
            500 for server errors.
        """
        try:
            # Validate device exists
            device = repo.get_device_by_id(device_id)
            if not device:
                return jsonify(error("Device not found.", code="NOT_FOUND")), 404

            cfg = get_config()
            ip = device.get("ip_address")
            if not ip:
                return jsonify(error("Device has no IP address.", code="INVALID_DEVICE")), 400

            # Execute ping
            ping_result = ping_ip(ip, timeout_ms=cfg.PING_TIMEOUT_MS)

            # Prepare update fields
            update_fields: Dict[str, Any] = {
                "status": ping_result["status"],
                # Store as datetime for Mongo; route uses UTC without timezone for consistency
                "last_ping": datetime.utcnow(),
            }

            # Persist update; ignore result if None (shouldn't be since we fetched)
            updated = repo.update_device(device_id, update_fields) or device

            return jsonify(
                success(
                    {
                        "device": updated,
                        "ping": ping_result,
                    },
                    message="Status checked",
                )
            )
        except ValueError as ve:
            _logger.info("Invalid device id on status check: %s", ve)
            return jsonify(error("Invalid device id.", code="INVALID_ID")), 400
        except Exception as exc:
            _logger.error("Error during status check for id=%s: %s", device_id, exc)
            return jsonify(error("Failed to check device status.", code="STATUS_CHECK_FAILED")), 500
