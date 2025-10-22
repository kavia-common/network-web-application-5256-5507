import pytest


def test_list_devices_initially_empty(client):
    res = client.get("/api/devices")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert isinstance(body.get("data"), list)
    assert body["data"] == []


def test_create_device_success(client):
    payload = {
        "name": "Core Router",
        "ip_address": "10.0.0.1",
        "device_type": "router",
        "location": "HQ",
    }
    res = client.post("/api/devices", json=payload)
    assert res.status_code == 201
    body = res.get_json()
    assert body["status"] == "success"
    dev = body["data"]
    assert dev["name"] == "Core Router"
    assert dev["ip_address"] == "10.0.0.1"
    assert "id" in dev


def test_create_device_validation_error(client):
    res = client.post("/api/devices", json={"name": ""})
    assert res.status_code == 400
    body = res.get_json()
    assert body["status"] == "error"
    assert body["code"] == "VALIDATION_ERROR"


def test_create_duplicate_ip_conflict(client):
    payload = {
        "name": "Edge Switch",
        "ip_address": "10.0.0.2",
        "device_type": "switch",
        "location": "Branch",
    }
    res1 = client.post("/api/devices", json=payload)
    assert res1.status_code == 201
    res2 = client.post("/api/devices", json=payload)
    assert res2.status_code == 409
    body = res2.get_json()
    assert body["status"] == "error"
    assert body["code"] == "DUPLICATE_IP"


def test_get_update_patch_delete_flow(client):
    # Create
    payload = {
        "name": "Server-1",
        "ip_address": "10.0.0.3",
        "device_type": "server",
        "location": "Lab",
    }
    created = client.post("/api/devices", json=payload).get_json()["data"]
    dev_id = created["id"]

    # Get
    res_get = client.get(f"/api/devices/{dev_id}")
    assert res_get.status_code == 200
    assert res_get.get_json()["data"]["name"] == "Server-1"

    # Get invalid id
    res_get_bad = client.get("/api/devices/not-an-id")
    assert res_get_bad.status_code == 400

    # Patch
    res_patch = client.patch(f"/api/devices/{dev_id}", json={"location": "Lab-2"})
    assert res_patch.status_code == 200
    assert res_patch.get_json()["data"]["location"] == "Lab-2"

    # Put (still uses validate_update semantics through _update)
    res_put = client.put(f"/api/devices/{dev_id}", json={"name": "Server-1A"})
    assert res_put.status_code == 200
    assert res_put.get_json()["data"]["name"] == "Server-1A"

    # Duplicate on update
    other = client.post(
        "/api/devices",
        json={
            "name": "Other",
            "ip_address": "10.0.0.4",
            "device_type": "router",
            "location": "HQ",
        },
    ).get_json()["data"]
    res_dup = client.patch(f"/api/devices/{dev_id}", json={"ip_address": "10.0.0.4"})
    assert res_dup.status_code == 409
    assert res_dup.get_json()["code"] == "DUPLICATE_IP"

    # Not found id
    from bson import ObjectId

    fake_id = str(ObjectId())
    res_nf = client.get(f"/api/devices/{fake_id}")
    assert res_nf.status_code == 404

    # Delete
    res_del = client.delete(f"/api/devices/{dev_id}")
    assert res_del.status_code == 204

    # Delete again -> 404
    res_del2 = client.delete(f"/api/devices/{dev_id}")
    assert res_del2.status_code == 404
