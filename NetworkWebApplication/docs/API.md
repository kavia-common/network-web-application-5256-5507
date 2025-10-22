# API Reference

This document describes the REST API exposed by the Flask backend. All endpoints are prefixed with /api.

## Conventions

- Content type: application/json
- Success response shape:
  { "status": "success", "message": "ok" | string, "data": any }
- Error response shape:
  { "status": "error", "message": string, "code"?: string, "details"?: any }
- IDs are MongoDB ObjectIds represented as hex strings.
- Standard error codes used: INVALID_ID, NOT_FOUND, VALIDATION_ERROR, DUPLICATE_IP, CREATE_FAILED, UPDATE_FAILED, DELETE_FAILED, LIST_FAILED, STATUS_CHECK_FAILED.

## Health

### GET /api/health

Returns a simple health payload with ping scheduler configuration.

Response 200:
- status: "success"
- data: { "uptime": true, "ping_enabled": boolean }

## Devices

Device fields:
- id: string (generated)
- name: string (required)
- ip_address: string IPv4 (required, unique)
- device_type: string enum [router, switch, server, other] (required)
- location: string (required)
- status: string optional [online, offline, unknown]
- last_ping: date (set by status checks or scheduler)

### GET /api/devices

List devices with optional filters.

Query params:
- name: string (exact match)
- ip_address: string (exact match)
- device_type: router|switch|server|other
- location: string (exact match)
- status: string

Response 200:
- data: [Device]

Errors:
- 500 LIST_FAILED

### POST /api/devices

Create a new device.

Body:
- name: string
- ip_address: string (IPv4)
- device_type: router|switch|server|other
- location: string
- status: optional string

Response 201:
- data: Device
- message: "Device created"

Errors:
- 400 VALIDATION_ERROR
- 409 DUPLICATE_IP
- 500 CREATE_FAILED

### GET /api/devices/{id}

Fetch a device by id.

Response 200:
- data: Device

Errors:
- 400 INVALID_ID
- 404 NOT_FOUND
- 500 GET_FAILED

### PUT /api/devices/{id}

Full update semantics (validated). In practice, the implementation validates provided fields and applies atomic updates.

Body: any subset of valid fields (name, ip_address, device_type, location, status)

Response 200:
- data: Device
- message: "Device updated"

Errors:
- 400 INVALID_ID or VALIDATION_ERROR
- 404 NOT_FOUND
- 409 DUPLICATE_IP
- 500 UPDATE_FAILED

### PATCH /api/devices/{id}

Partial update, identical semantics to PUT endpoint above.

Response 200:
- data: Device
- message: "Device updated"

Errors: same as PUT.

### DELETE /api/devices/{id}

Delete a device by id.

Response 204:
- No body

Errors:
- 400 INVALID_ID
- 404 NOT_FOUND
- 500 DELETE_FAILED

## Device Status

### GET /api/devices/{id}/status

Manually ping the device and update status and last_ping.

Response 200:
- data:
  - device: Device (updated)
  - ping:
    - status: "online" | "offline"
    - latency_ms: float | null
    - timestamp: ISO 8601 string

Errors:
- 400 INVALID_ID or INVALID_DEVICE
- 404 NOT_FOUND
- 500 STATUS_CHECK_FAILED

## Notes

- Background scheduler (if enabled via PING_ENABLED) periodically pings all devices and updates status/last_ping.
- Unique index is enforced on ip_address; attempting to create or update to a duplicate will return code DUPLICATE_IP.

Sources: backend/app.py, backend/resources/devices.py, backend/resources/status.py, backend/models/device_repository.py, backend/services/db.py, backend/services/ping.py
