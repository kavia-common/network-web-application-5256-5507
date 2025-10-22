"""Validation and normalization utilities for device payloads.

This module provides helpers for validating device payloads used by the API and
repositories. It enforces:
- Non-empty name and location (after trimming whitespace)
- Valid IPv4 address format
- device_type restricted to one of: router, switch, server, other
- Normalization (trimming whitespace, lowercasing device_type, collapsing spaces)

Exports:
- ValidationError
- DuplicateIPError
- normalize_payload
- validate_create
- validate_update
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Tuple
import ipaddress

# Allowed device types (lowercase)
ALLOWED_DEVICE_TYPES = {"router", "switch", "server", "other"}


class ValidationError(Exception):
    """Raised when payload validation fails with message suitable for API responses."""


class DuplicateIPError(Exception):
    """Raised when attempting to create/update a device using an already-registered IP address."""


def _is_valid_ipv4(ip: str) -> bool:
    """Return True if the provided string is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ip)
        return True
    except Exception:
        return False


def _clean_str(value: Any, max_len: Optional[int] = None) -> str:
    """Convert to string, trim whitespace, and optionally enforce max length."""
    if value is None:
        return ""
    s = str(value).strip()
    if max_len is not None and len(s) > max_len:
        s = s[:max_len].strip()
    return s


# PUBLIC_INTERFACE
def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize incoming device payload by trimming whitespace and standardizing fields.

    Normalizations:
    - name: trimmed, max length 100
    - ip_address: trimmed
    - device_type: lowercased, trimmed
    - location: trimmed, max length 100

    Args:
        payload: Raw payload dict (typically from request.json)

    Returns:
        A new normalized payload dict (does not mutate the input).
    """
    data = dict(payload or {})

    if "name" in data:
        data["name"] = _clean_str(data["name"], max_len=100)

    if "ip_address" in data:
        # Do not alter dots or digits; just strip spaces
        data["ip_address"] = _clean_str(data["ip_address"])

    if "device_type" in data:
        data["device_type"] = _clean_str(data["device_type"]).lower()

    if "location" in data:
        data["location"] = _clean_str(data["location"], max_len=100)

    # Optional fields normalization (if provided)
    if "status" in data and data["status"] is not None:
        data["status"] = _clean_str(data["status"]).lower()

    return data


def _validate_common(data: Dict[str, Any], require_all_fields: bool) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Validate fields common to both create and update operations.

    Args:
        data: Normalized payload dictionary.
        require_all_fields: If True, all required fields must be present; otherwise partial updates are allowed.

    Returns:
        Tuple of (clean_data, errors)
    """
    errors: Dict[str, str] = {}
    clean: Dict[str, Any] = {}

    def require(field: str) -> bool:
        return require_all_fields or (field in data)

    # name
    if require("name"):
        name = data.get("name", "")
        if not name:
            errors["name"] = "Name is required and cannot be empty."
        else:
            clean["name"] = name

    # ip_address
    if require("ip_address"):
        ip = data.get("ip_address", "")
        if not ip:
            errors["ip_address"] = "IP address is required and cannot be empty."
        elif not _is_valid_ipv4(ip):
            errors["ip_address"] = "IP address must be a valid IPv4 address."
        else:
            clean["ip_address"] = ip

    # device_type
    if require("device_type"):
        dtype = data.get("device_type", "")
        if not dtype:
            errors["device_type"] = "Device type is required and cannot be empty."
        elif dtype not in ALLOWED_DEVICE_TYPES:
            errors["device_type"] = f"Device type must be one of: {', '.join(sorted(ALLOWED_DEVICE_TYPES))}."
        else:
            clean["device_type"] = dtype

    # location
    if require("location"):
        loc = data.get("location", "")
        if not loc:
            errors["location"] = "Location is required and cannot be empty."
        else:
            clean["location"] = loc

    # Optional fields passthrough (if present and non-empty strings)
    if "status" in data and isinstance(data["status"], str) and data["status"]:
        clean["status"] = data["status"]

    return clean, errors


# PUBLIC_INTERFACE
def validate_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate payload for creating a new device.

    Required fields: name, ip_address, device_type, location.

    Args:
        payload: Input payload dict.

    Returns:
        Cleaned and validated payload dict.

    Raises:
        ValidationError: If validation fails. Message is suitable for API response.
    """
    normalized = normalize_payload(payload)
    clean, errors = _validate_common(normalized, require_all_fields=True)

    if errors:
        # Combine messages into a readable, client-facing error text
        details = "; ".join([f"{k}: {v}" for k, v in errors.items()])
        raise ValidationError(f"Invalid device payload: {details}")

    return clean


# PUBLIC_INTERFACE
def validate_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate payload for updating an existing device.

    All fields are optional, but if provided, must meet the same validation rules as create().

    Args:
        payload: Input payload dict.

    Returns:
        Cleaned and validated partial payload dict (only includes valid provided fields).

    Raises:
        ValidationError: If provided fields are invalid or payload is empty.
    """
    normalized = normalize_payload(payload)
    if not normalized:
        raise ValidationError("No fields provided for update.")

    clean, errors = _validate_common(normalized, require_all_fields=False)

    if errors:
        details = "; ".join([f"{k}: {v}" for k, v in errors.items()])
        raise ValidationError(f"Invalid device update payload: {details}")

    if not clean:
        # Payload had fields but after validation nothing valid remained (e.g., empty strings)
        raise ValidationError("No valid fields provided for update.")

    return clean
