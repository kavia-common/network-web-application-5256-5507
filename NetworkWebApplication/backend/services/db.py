import logging
from typing import Optional

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from ..config import get_config

_logger = logging.getLogger(__name__)

# Internal singleton references
_client: Optional[MongoClient] = None
_db: Optional[Database] = None
_collection: Optional[Collection] = None


def _init_client() -> MongoClient:
    """
    Initialize and return a singleton MongoClient using environment configuration.

    Raises:
        ValueError: If MONGODB_URI is missing or empty.
    """
    global _client
    if _client is not None:
        return _client

    cfg = get_config()
    if not cfg.MONGODB_URI:
        # Clear error to instruct operator to set env variable
        raise ValueError(
            "MONGODB_URI is not configured. Please set the MONGODB_URI environment variable."
        )

    _logger.info("Initializing MongoClient for database operations.")
    # MongoClient performs lazy connections; let it manage pooling internally.
    _client = MongoClient(cfg.MONGODB_URI)
    return _client


def _init_db() -> Database:
    """
    Initialize and return a singleton Database instance using MONGODB_DB.
    """
    global _db
    if _db is not None:
        return _db

    client = _init_client()
    cfg = get_config()
    _db = client[cfg.MONGODB_DB]
    _logger.debug("Selected MongoDB database: %s", cfg.MONGODB_DB)
    return _db


# PUBLIC_INTERFACE
def get_db() -> Database:
    """Return a MongoDB Database instance configured via environment variables."""
    return _init_db()


# PUBLIC_INTERFACE
def get_collection(name: Optional[str] = None) -> Collection:
    """
    Return the MongoDB Collection instance.

    Args:
        name: Optional collection name. If not provided, uses MONGODB_COLLECTION from env.

    Returns:
        pymongo.collection.Collection: The requested collection instance.
    """
    global _collection
    if name:
        # If an explicit collection name is requested, return that on demand
        _logger.debug("Accessing explicit collection: %s", name)
        return get_db()[name]

    if _collection is not None:
        return _collection

    cfg = get_config()
    col_name = cfg.MONGODB_COLLECTION
    _collection = get_db()[col_name]
    _logger.debug("Using default collection: %s", col_name)
    return _collection


# PUBLIC_INTERFACE
def ensure_indexes() -> None:
    """
    Ensure required indexes exist on the devices collection.

    - Unique index on ip_address
    - Non-unique indexes on device_type and status

    Safe to call multiple times (idempotent).
    """
    try:
        col = get_collection()  # default collection from env
    except ValueError as e:
        # If Mongo is not configured yet, log and re-raise for startup visibility.
        _logger.error("Database configuration error: %s", e)
        raise

    _logger.info("Ensuring MongoDB indexes on collection '%s'.", col.name)

    # Unique index on ip_address
    col.create_index([("ip_address", ASCENDING)], name="uniq_ip_address", unique=True)

    # Non-unique indexes for common query fields
    col.create_index([("device_type", ASCENDING)], name="idx_device_type")
    col.create_index([("status", ASCENDING)], name="idx_status")

    _logger.info("MongoDB indexes ensured successfully.")
