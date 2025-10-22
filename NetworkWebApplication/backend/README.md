# Network Web Application - Backend

Flask + Flask-RESTful backend scaffold for the Network Web Application.

## Quick start

1. Create and activate a virtual environment (optional).
2. Install dependencies:
   pip install -r requirements.txt
3. Run development server:
   python -m backend.app

The server will run on port APP_PORT (default 5000).

## Environment variables

- MONGODB_URI: Mongo connection string (optional for initial run).
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

## Static files

If the React frontend has been built to frontend/build, the backend will serve it. If not present, visiting `/` returns a JSON message and a link to `/api/health`.
