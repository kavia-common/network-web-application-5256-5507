import logging
from typing import Any, Dict, Optional

from flask import request, jsonify
from flask_restful import Resource

from ..models import device_repository as repo
from ..services.validation import ValidationError, DuplicateIPError, normalize_payload, validate_create, validate_update
from ..utils.responses import success, error

_logger = logging.getLogger(__name__)


class DevicesListResource(Resource):
    """Resource for operations on the collection of devices.

    Supports:
    - GET /api/devices: List devices with optional filters via query params.
    - POST /api/devices: Create a new device with validation and duplicate IP prevention.
    """

    # PUBLIC_INTERFACE
    def get(self):
        """List devices with optional filters.

        Query parameters:
        - name: exact match for name (string)
        - ip_address: exact match for IP address (string)
        - device_type: filter by device type (router|switch|server|other)
        - location: exact match for location (string)
        - status: optional status filter (string)

        Returns:
            JSON response with status, message, and data:list of devices.
        """
        try:
            # Build filters from allowed query params. Any other params are ignored.
            filters: Dict[str, Any] = {}
            allowed = ("name", "ip_address", "device_type", "location", "status")
            for key in allowed:
                val = request.args.get(key)
                if val is not None and val != "":
                    filters[key] = val

            # Note: "name contains" style search can later be mapped to regex in repo if needed
            devices = repo.list_devices(filters or None)
            return jsonify(success(devices))
        except Exception as exc:
            _logger.error("Error listing devices: %s", exc)
            return jsonify(error("Failed to fetch devices.", code="LIST_FAILED")), 500

    # PUBLIC_INTERFACE
    def post(self):
        """Create a new device.

        Request body (JSON):
        - name: string (required)
        - ip_address: IPv4 string (required, unique)
        - device_type: router|switch|server|other (required)
        - location: string (required)
        - status: optional string

        Returns:
            201 with created device on success,
            400 for validation errors,
            409 when duplicate IP address is detected,
            500 for other server errors.
        """
        try:
            payload = request.get_json(silent=True) or {}
            # Run validation explicitly here to return 400 on validation errors
            clean = validate_create(payload)
            created = repo.create_device(clean)
            return jsonify(success(created, message="Device created")), 201
        except ValidationError as ve:
            _logger.info("Validation error on device create: %s", ve)
            return jsonify(error(str(ve), code="VALIDATION_ERROR")), 400
        except DuplicateIPError as dup:
            _logger.info("Duplicate IP on create: %s", dup)
            return jsonify(error("Duplicate IP address.", code="DUPLICATE_IP")), 409
        except Exception as exc:
            _logger.error("Server error creating device: %s", exc)
            return jsonify(error("Failed to create device.", code="CREATE_FAILED")), 500


class DeviceResource(Resource):
    """Resource for operations on an individual device by id.

    Supports:
    - GET /api/devices/<id>: Get device by id.
    - PUT /api/devices/<id>: Full update (validated).
    - PATCH /api/devices/<id>: Partial update (validated).
    - DELETE /api/devices/<id>: Delete device by id.
    """

    # PUBLIC_INTERFACE
    def get(self, device_id: str):
        """Fetch a device by id.

        Path params:
        - device_id: string ObjectId hex

        Returns:
            200 with device if found,
            404 if not found,
            400 for invalid id,
            500 for server error.
        """
        try:
            device = repo.get_device_by_id(device_id)
            if not device:
                return jsonify(error("Device not found.", code="NOT_FOUND")), 404
            return jsonify(success(device))
        except ValueError as ve:
            _logger.info("Invalid id on GET: %s", ve)
            return jsonify(error("Invalid device id.", code="INVALID_ID")), 400
        except Exception as exc:
            _logger.error("Error fetching device %s: %s", device_id, exc)
            return jsonify(error("Failed to fetch device.", code="GET_FAILED")), 500

    # PUBLIC_INTERFACE
    def put(self, device_id: str):
        """Update an existing device by replacing/updating provided fields (full update semantics).

        Body is validated; duplicate IP updates are prevented.

        Returns:
            200 with updated device,
            404 if device not found,
            400 for invalid id or validation error,
            409 for duplicate IP conflict,
            500 for other errors.
        """
        return self._update(device_id, method="PUT")

    # PUBLIC_INTERFACE
    def patch(self, device_id: str):
        """Partially update an existing device.

        Returns:
            200 with updated device,
            404 if device not found,
            400 for invalid id or validation error,
            409 for duplicate IP conflict,
            500 for other errors.
        """
        return self._update(device_id, method="PATCH")

    def _update(self, device_id: str, method: str = "PATCH"):
        """Internal helper to handle PUT/PATCH with shared logic."""
        try:
            payload = request.get_json(silent=True) or {}
            clean = validate_update(payload)
            updated = repo.update_device(device_id, clean)
            if not updated:
                return jsonify(error("Device not found.", code="NOT_FOUND")), 404
            return jsonify(success(updated, message="Device updated"))
        except ValidationError as ve:
            _logger.info("Validation error on %s: %s", method, ve)
            return jsonify(error(str(ve), code="VALIDATION_ERROR")), 400
        except DuplicateIPError as dup:
            _logger.info("Duplicate IP on %s: %s", method, dup)
            return jsonify(error("Duplicate IP address.", code="DUPLICATE_IP")), 409
        except ValueError as ve:
            _logger.info("Invalid id on %s: %s", method, ve)
            return jsonify(error("Invalid device id.", code="INVALID_ID")), 400
        except Exception as exc:
            _logger.error("Server error on %s for id=%s: %s", method, device_id, exc)
            return jsonify(error("Failed to update device.", code="UPDATE_FAILED")), 500

    # PUBLIC_INTERFACE
    def delete(self, device_id: str):
        """Delete a device by id.

        Returns:
            204 on successful deletion,
            404 if not found,
            400 for invalid id,
            500 for other errors.
        """
        try:
            deleted = repo.delete_device(device_id)
            if not deleted:
                return jsonify(error("Device not found.", code="NOT_FOUND")), 404
            # 204 No Content: do not include body; but keep standardized approach by returning empty response.
            return ("", 204)
        except ValueError as ve:
            _logger.info("Invalid id on DELETE: %s", ve)
            return jsonify(error("Invalid device id.", code="INVALID_ID")), 400
        except Exception as exc:
            _logger.error("Error deleting device %s: %s", device_id, exc)
            return jsonify(error("Failed to delete device.", code="DELETE_FAILED")), 500
