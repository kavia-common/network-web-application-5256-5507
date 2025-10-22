from unittest.mock import patch, MagicMock

import pytest


def _create_device(client, ip="203.0.113.10"):
    payload = {
        "name": "PingTarget",
        "ip_address": ip,
        "device_type": "router",
        "location": "TestNet",
    }
    return client.post("/api/devices", json=payload).get_json()["data"]


@patch("backend.services.ping.ping")
def test_status_online_updates_device(mock_ping, client):
    # Mock pythonping result: online with RTT
    m = MagicMock()
    m.success.return_value = True
    m.rtt_avg = 0.005
    mock_ping.return_value = m

    d = _create_device(client, ip="198.51.100.20")
    res = client.get(f"/api/devices/{d['id']}/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert "device" in body["data"] and "ping" in body["data"]
    assert body["data"]["ping"]["status"] == "online"

    # Device should now have status updated
    res_get = client.get(f"/api/devices/{d['id']}")
    assert res_get.status_code == 200
    dev = res_get.get_json()["data"]
    assert dev["status"] == "online"
    # last_ping presence; type is datetime in DB, but serialized returns string? Repo returns raw; ensure field exists.
    assert "last_ping" in dev


@patch("backend.services.ping.ping")
def test_status_offline_and_invalid_id(mock_ping, client):
    # offline
    m = MagicMock()
    m.success.return_value = False
    m.rtt_avg = None
    mock_ping.return_value = m

    d = _create_device(client, ip="203.0.113.30")
    res = client.get(f"/api/devices/{d['id']}/status")
    assert res.status_code == 200
    assert res.get_json()["data"]["ping"]["status"] == "offline"

    # invalid id
    res_bad = client.get("/api/devices/not-an-id/status")
    assert res_bad.status_code == 400


def test_status_not_found(client):
    # Random ObjectId not in DB
    from bson import ObjectId

    fake_id = str(ObjectId())
    res = client.get(f"/api/devices/{fake_id}/status")
    assert res.status_code == 404
