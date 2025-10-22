# Environment Variables

The backend reads configuration from environment variables (via python-dotenv if a .env file is present). This document lists variables, defaults, and examples.

## MongoDB

- MONGODB_URI
  - Description: MongoDB connection string (required for DB operations)
  - Default: "" (empty). If empty, attempting DB access raises a clear error.
  - Example: mongodb://localhost:27017
- MONGODB_DB
  - Description: Database name
  - Default: network_devices
  - Example: network_devices
- MONGODB_COLLECTION
  - Description: Collection name for devices
  - Default: devices
  - Example: devices

## Ping and Scheduler

- PING_ENABLED
  - Description: Enables background scheduler to ping devices periodically
  - Default: true
  - Accepted truthy: 1, true, yes, y (case-insensitive)
- PING_INTERVAL_SECONDS
  - Description: Interval between scheduled pings
  - Default: 300
  - Example: 120
- PING_TIMEOUT_MS
  - Description: Timeout per ping (milliseconds) per device
  - Default: 1000
  - Example: 1500

## Server and Flask

- APP_PORT
  - Description: Flask server port when running python -m backend.app
  - Default: 5000
- FLASK_DEBUG
  - Description: Enables Flask debug mode
  - Default: false
  - Accepted truthy: 1, true, yes, y
- FLASK_ENV
  - Description: Flask environment
  - Default: production
  - Example: development
- LOG_LEVEL
  - Description: Logging level for the app logger
  - Default: INFO
  - Example: DEBUG

## Frontend Build Serving

- In production, Flask serves static files from frontend/build if present. Ensure you run npm run build in frontend/ prior to starting Flask in production mode.

## .env Example

Create NetworkWebApplication/.env with:

- MONGODB_URI=mongodb://localhost:27017
- MONGODB_DB=network_devices
- MONGODB_COLLECTION=devices
- APP_PORT=5000
- FLASK_DEBUG=true
- PING_ENABLED=true
- PING_INTERVAL_SECONDS=300
- PING_TIMEOUT_MS=1000
- LOG_LEVEL=INFO

## Notes

- In tests, pytest fixtures set PING_ENABLED=false by default to avoid scheduler startup.
- If MONGODB_URI is not set and DB is accessed, backend/services/db.py will raise a clear error instructing you to configure it.

Sources: backend/config.py, backend/services/db.py, backend/app.py
