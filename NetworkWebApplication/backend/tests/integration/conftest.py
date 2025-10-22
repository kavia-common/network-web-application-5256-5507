import os
import types
import mongomock
import pytest

from backend.app import create_app
from backend.services import db as db_service


@pytest.fixture(scope="session", autouse=True)
def set_test_env(monkeypatch):
    # Disable background scheduler and ensure consistent timeouts
    monkeypatch.setenv("PING_ENABLED", "false")
    monkeypatch.setenv("PING_INTERVAL_SECONDS", "300")
    monkeypatch.setenv("PING_TIMEOUT_MS", "1000")
    # Provide a dummy URI so db._init_client() would not be called in tests that patch get_collection
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost/dummy")
    monkeypatch.setenv("MONGODB_DB", "network_devices_test")
    monkeypatch.setenv("MONGODB_COLLECTION", "devices_test")
    yield


@pytest.fixture()
def mock_collection(monkeypatch):
    """
    Provide a mongomock collection and patch backend.services.db.get_collection
    to return this instance. Also bypass ensure_indexes to avoid real pymongo calls.
    """
    client = mongomock.MongoClient()
    db = client[os.getenv("MONGODB_DB", "network_devices_test")]
    col = db[os.getenv("MONGODB_COLLECTION", "devices_test")]
    # Create unique index behavior for ip_address in mongomock
    col.create_index("ip_address", unique=True)

    def _get_collection(name=None):
        return db[name] if name else col

    monkeypatch.setattr(db_service, "get_collection", _get_collection, raising=True)

    # Ensure internal cached _collection doesn't interfere
    if hasattr(db_service, "_collection"):
        monkeypatch.setattr(db_service, "_collection", None, raising=False)
    if hasattr(db_service, "_db"):
        monkeypatch.setattr(db_service, "_db", None, raising=False)
    if hasattr(db_service, "_client"):
        monkeypatch.setattr(db_service, "_client", None, raising=False)

    yield col


@pytest.fixture()
def app(mock_collection, monkeypatch):
    """
    Build a Flask test app using create_app with patched DB and disabled scheduler.
    """
    # Prevent scheduler from starting by forcing PING_ENABLED=false via env
    monkeypatch.setenv("PING_ENABLED", "false")
    application = create_app()
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
