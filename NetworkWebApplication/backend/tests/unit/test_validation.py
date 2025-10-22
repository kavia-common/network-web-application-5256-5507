import pytest

from backend.services.validation import (
    normalize_payload,
    validate_create,
    validate_update,
    ValidationError,
    ALLOWED_DEVICE_TYPES,
)


def test_normalize_payload_trims_and_lowercases():
    payload = {
        "name": "  Core Router  ",
        "ip_address": " 192.168.1.1 ",
        "device_type": "  SERVER ",
        "location": "  HQ  ",
        "status": "  ONLINE ",
    }
    norm = normalize_payload(payload)
    assert norm["name"] == "Core Router"
    assert norm["ip_address"] == "192.168.1.1"
    assert norm["device_type"] == "server"
    assert norm["location"] == "HQ"
    assert norm["status"] == "online"


def test_validate_create_success():
    payload = {
        "name": "Edge Switch",
        "ip_address": "10.0.0.2",
        "device_type": "switch",
        "location": "Branch A",
    }
    clean = validate_create(payload)
    assert clean == payload


@pytest.mark.parametrize(
    "payload, expected_substring",
    [
        (
            {"ip_address": "10.0.0.2", "device_type": "switch", "location": "Branch"},
            "name",
        ),
        (
            {"name": "X", "device_type": "switch", "location": "Branch"},
            "ip address",
        ),
        (
            {"name": "X", "ip_address": "bad-ip", "device_type": "switch", "location": "Branch"},
            "valid IPv4",
        ),
        (
            {"name": "X", "ip_address": "10.0.0.2", "location": "Branch"},
            "device type",
        ),
        (
            {"name": "X", "ip_address": "10.0.0.2", "device_type": "server"},
            "location",
        ),
        (
            {"name": "X", "ip_address": "10.0.0.2", "device_type": "invalid", "location": "L"},
            "one of",
        ),
    ],
)
def test_validate_create_errors(payload, expected_substring):
    with pytest.raises(ValidationError) as e:
        validate_create(payload)
    assert expected_substring.lower() in str(e.value).lower()


def test_validate_update_partial_success_and_rules():
    # valid partial
    partial = {"name": "New Name"}
    clean = validate_update(partial)
    assert clean == {"name": "New Name"}

    # empty payload
    with pytest.raises(ValidationError):
        validate_update({})

    # invalid ip
    with pytest.raises(ValidationError) as e:
        validate_update({"ip_address": "bad"})
    assert "valid IPv4" in str(e.value)

    # invalid device_type
    with pytest.raises(ValidationError):
        validate_update({"device_type": "Nope"})

    # trimming normalization still enforced
    clean2 = validate_update({"location": "  HQ  "})
    assert clean2["location"] == "HQ"


def test_allowed_device_types_are_sane():
    assert {"router", "switch", "server", "other"} == ALLOWED_DEVICE_TYPES
