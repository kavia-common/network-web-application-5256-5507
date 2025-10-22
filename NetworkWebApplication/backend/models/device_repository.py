"""
Device repository: provides CRUD operations for the devices collection.

This is a pure data-access layer that:
- Uses services.db.get_collection() to access MongoDB
- Converts between Mongo ObjectId and string id
- Enforces unique ip_address (maps duplicate key error to DuplicateIPError)
- Returns standardized dicts via _serialize()
- Performs atomic updates for PUT/PATCH operations

Public functions:
- list_devices(filters)
- get_device_by_id(id)
- create_device(payload)
- update_device(id, payload)
- delete_device(id)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import logging
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from bson.errors import InvalidId

from ..services.db import get_collection
from ..services.validation import validate_create, validate_update, DuplicateIPError

_logger = logging.getLogger(__name__)


def _get_devices_collection() -> Collection:
    """Internal helper to retrieve the devices collection using configured defaults."""
    return get_collection()  # default collection name comes from env via services.db


def _to_object_id(id_str: str) -> ObjectId:
    """Convert a hex string id into an ObjectId, raising ValueError on invalid format."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError) as exc:
        raise ValueError("Invalid id format") from exc


def _serialize(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Standardize Mongo document into API-friendly dict.

    - Renames _id (ObjectId) to string id
    - Returns None if doc is None
    """
    if not doc:
        return None
    data = dict(doc)
    oid = data.pop("_id", None)
    if isinstance(oid, ObjectId):
        data["id"] = str(oid)
    elif oid is not None:
        # fallback to string conversion if some other type sneaks in
        data["id"] = str(oid)
    return data


# PUBLIC_INTERFACE
def list_devices(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return a list of devices matching optional filters.

    Args:
        filters: Optional query filters (fields like device_type, status, location, name).
                 Values should be exact matches; complex queries can be added later.

    Returns:
        List of serialized device dictionaries.
    """
    query: Dict[str, Any] = {}
    if filters:
        # Only allow known fields to prevent injection of operators unless explicitly intended
        allowed = {"name", "ip_address", "device_type", "location", "status"}
        for k, v in (filters or {}).items():
            if k in allowed and v is not None:
                query[k] = v

    try:
        col = _get_devices_collection()
        cursor = col.find(query)
        return [_serialize(d) for d in cursor]
    except PyMongoError as exc:
        _logger.error("Failed to list devices: %s", exc)
        # Re-raise as a generic exception to be handled by higher layers (resources)
        raise


# PUBLIC_INTERFACE
def get_device_by_id(id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single device by its string id.

    Args:
        id: The device id as a hex string.

    Returns:
        The serialized device dict if found; otherwise None.

    Raises:
        ValueError: If id is not a valid ObjectId string.
    """
    oid = _to_object_id(id)
    try:
        col = _get_devices_collection()
        doc = col.find_one({"_id": oid})
        return _serialize(doc)
    except PyMongoError as exc:
        _logger.error("Failed to fetch device by id=%s: %s", id, exc)
        raise


# PUBLIC_INTERFACE
def create_device(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new device document after validation.

    Args:
        payload: Raw input payload with device fields.

    Returns:
        The newly created serialized device dict.

    Raises:
        DuplicateIPError: If ip_address violates the unique index.
        Exception: For other database-related errors.
    """
    clean = validate_create(payload)
    try:
        col = _get_devices_collection()
        # Insert and fetch created doc atomically using inserted_id
        result = col.insert_one(clean)
        created = col.find_one({"_id": result.inserted_id})
        return _serialize(created) or {}
    except DuplicateKeyError as dup:
        # Identify duplicate on ip_address unique index
        # Most drivers include index name or key pattern; map all duplicate key errors here.
        _logger.info("Duplicate IP address on create: %s", dup)
        raise DuplicateIPError("A device with this IP address already exists.") from dup
    except PyMongoError as exc:
        _logger.error("Failed to create device: %s", exc)
        raise


# PUBLIC_INTERFACE
def update_device(id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing device by id using atomic update semantics.

    This method supports both full and partial updates. Provided fields are validated and
    applied atomically via $set. Unknown/empty fields are ignored by validation.

    Args:
        id: Device id as hex string.
        payload: Partial or full payload to update.

    Returns:
        The updated device as a serialized dict, or None if not found.

    Raises:
        ValueError: If id format is invalid.
        DuplicateIPError: If updating ip_address to an existing value.
        Exception: For other database-related errors.
    """
    oid = _to_object_id(id)
    clean = validate_update(payload)

    if not clean:
        # validate_update would have already raised, but keep a defensive check
        return get_device_by_id(id)

    try:
        col = _get_devices_collection()

        # Use find_one_and_update for atomic update and returning the new document
        updated = col.find_one_and_update(
            {"_id": oid},
            {"$set": clean},
            return_document=True,  # Return the updated document (pymongo>=4 uses ReturnDocument.AFTER; True works via bool cast)
        )
        # If using explicit enum is preferred, uncomment next lines and replace return_document=True above:
        # from pymongo import ReturnDocument
        # updated = col.find_one_and_update({"_id": oid}, {"$set": clean}, return_document=ReturnDocument.AFTER)

        return _serialize(updated)
    except DuplicateKeyError as dup:
        _logger.info("Duplicate IP address on update for id=%s: %s", id, dup)
        raise DuplicateIPError("A device with this IP address already exists.") from dup
    except PyMongoError as exc:
        _logger.error("Failed to update device id=%s: %s", id, exc)
        raise


# PUBLIC_INTERFACE
def delete_device(id: str) -> bool:
    """Delete a device by id.

    Args:
        id: Device id as hex string.

    Returns:
        True if a document was deleted; False if no document matched.

    Raises:
        ValueError: If id is invalid.
        Exception: For database errors.
    """
    oid = _to_object_id(id)
    try:
        col = _get_devices_collection()
        res = col.delete_one({"_id": oid})
        return res.deleted_count > 0
    except PyMongoError as exc:
        _logger.error("Failed to delete device id=%s: %s", id, exc)
        raise
