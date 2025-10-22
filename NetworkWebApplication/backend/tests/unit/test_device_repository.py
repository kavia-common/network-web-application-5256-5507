import pytest
from bson import ObjectId

from backend.models import device_repository as repo
from backend.services.validation import DuplicateIPError
from backend.tests.integration.conftest import mock_collection  # reuse fixture


@pytest.fixture()
def sample_device_payload():
    return {
        "name": "Server-1",
        "ip_address": "192.168.10.10",
        "device_type": "server",
        "location": "Lab",
    }


def test_create_and_get_device(mock_collection, sample_device_payload, monkeypatch):
    created = repo.create_device(sample_device_payload)
    assert created["id"]
    assert created["name"] == "Server-1"
    # Fetch by id
    fetched = repo.get_device_by_id(created["id"])
    assert fetched["ip_address"] == "192.168.10.10"


def test_list_devices_filters(mock_collection, sample_device_payload):
    repo.create_device(sample_device_payload)
    repo.create_device(
        {
            "name": "Switch-1",
            "ip_address": "192.168.10.11",
            "device_type": "switch",
            "location": "HQ",
        }
    )
    all_items = repo.list_devices()
    assert len(all_items) == 2

    only_switch = repo.list_devices({"device_type": "switch"})
    assert len(only_switch) == 1
    assert only_switch[0]["device_type"] == "switch"


def test_duplicate_ip_handling_on_create(mock_collection, sample_device_payload):
    repo.create_device(sample_device_payload)
    with pytest.raises(DuplicateIPError):
        repo.create_device(sample_device_payload)


def test_update_device_and_duplicate_on_update(mock_collection):
    a = repo.create_device(
        {"name": "A", "ip_address": "10.0.0.1", "device_type": "router", "location": "HQ"}
    )
    b = repo.create_device(
        {"name": "B", "ip_address": "10.0.0.2", "device_type": "router", "location": "HQ"}
    )
    # Update name and location
    updated = repo.update_device(a["id"], {"name": "A2", "location": "HQ-2"})
    assert updated["name"] == "A2"
    assert updated["location"] == "HQ-2"

    # Attempt to update IP to duplicate
    with pytest.raises(DuplicateIPError):
        repo.update_device(a["id"], {"ip_address": "10.0.0.2"})


def test_delete_device(mock_collection):
    c = repo.create_device(
        {"name": "C", "ip_address": "10.0.0.3", "device_type": "server", "location": "DC"}
    )
    ok = repo.delete_device(c["id"])
    assert ok is True
    assert repo.get_device_by_id(c["id"]) is None

    # delete again should be False
    assert repo.delete_device(c["id"]) is False


def test_invalid_objectid_raises_valueerror_on_get_and_delete(mock_collection):
    with pytest.raises(ValueError):
        repo.get_device_by_id("not-an-id")
    with pytest.raises(ValueError):
        repo.delete_device("still-bad")
