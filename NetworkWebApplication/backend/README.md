# Network Web Application - Backend

Flask + Flask-RESTful backend for the Network Web Application. This backend is now a standalone API container; it does not serve the React frontend. Use the separate frontend container (React dev server or static host) and point it to this API.

## Quick start

1. Create and activate a virtual environment (optional).

2. Install dependencies:
   pip install -r requirements.txt

3. Run development server (Flask):
   python -m backend.app
   - Server listens on 0.0.0.0:APP_PORT (default 5000)

4. Production (Gunicorn):
   gunicorn -w 3 -b 0.0.0.0:${APP_PORT:-5000} backend.wsgi:app

## CORS

CORS is enabled for API routes under /api. By default, all origins are allowed for development ("*"). For production, configure your reverse proxy or set up a stricter origin policy (update app to read a FRONTEND_ORIGIN env when introduced).

## Environment variables

- MONGODB_URI: Mongo connection string (required for DB operations)
- MONGODB_DB: Database name (default: network_devices)
- MONGODB_COLLECTION: Collection name (default: devices)
- PING_ENABLED: Enable periodic ping checks (default: true)
- PING_INTERVAL_SECONDS: Ping interval seconds (default: 300)
- PING_TIMEOUT_MS: Ping timeout in ms (default: 1000)
- APP_PORT: Backend port (default: 5000)
- LOG_LEVEL: Logging level (default: INFO)
- FLASK_DEBUG: Debug flag (default: false)
- FLASK_ENV: Flask environment (default: production)

## Endpoints

- GET /api/health — health check returning {"status":"success","message":"ok","data":{...}}
- GET /api/devices — list devices
- POST /api/devices — create device
- GET /api/devices/{id} — get device
- PATCH/PUT /api/devices/{id} — update device
- DELETE /api/devices/{id} — delete device
- GET /api/devices/{id}/status — ping device and update status

## Notes

- This backend no longer serves React static assets or catch-all routes. Only /api endpoints and /api health/index routes are exposed.
- Ensure your frontend points to this backend API (e.g., REACT_APP_API_BASE=http://localhost:5000/api or proxy setup during development).
