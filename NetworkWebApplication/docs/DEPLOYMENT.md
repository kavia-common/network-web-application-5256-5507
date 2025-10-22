# Deployment and CI/CD

This document explains how to serve the application in production and outlines a CI/CD approach.

## Production Serving

In production, Flask serves both:
- The REST API under /api
- The React static build from frontend/build

### Build frontend

From NetworkWebApplication/frontend/:

- npm install
- npm run build

This generates frontend/build.

### Run Flask in production

From NetworkWebApplication/:

- Ensure environment variables are set (see docs/ENV.md). At minimum: MONGODB_URI.
- Start the app:
  - python -m backend.app

The app listens on APP_PORT (default 5000). Visit http://localhost:5000.

### WSGI servers

For hardened production, use a WSGI server such as gunicorn or uWSGI.

Example with gunicorn (install gunicorn in your environment):
- gunicorn -w 3 -b 0.0.0.0:5000 backend.wsgi:app

The module backend/wsgi.py exposes app.

### Health and Diagnostics

- Health check: GET /api/health
- API index: GET /api
- Logs: controlled by LOG_LEVEL (INFO by default)

## Environment Management

- Keep secrets such as MONGODB_URI out of source control.
- Use environment variables or a secure secrets manager in your hosting environment.
- Ensure the following are configured:
  - MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION
  - PING_ENABLED, PING_INTERVAL_SECONDS, PING_TIMEOUT_MS
  - APP_PORT, LOG_LEVEL, FLASK_ENV, FLASK_DEBUG

## Background Scheduler

- Controlled by PING_ENABLED. When true, the app starts a background job to ping all devices at PING_INTERVAL_SECONDS and update status/last_ping.
- If Mongo is not configured, ensure PING_ENABLED=false or set the database variables before starting.

## Zero-Downtime Considerations

- Build the frontend ahead of time.
- Start the WSGI server with multiple workers.
- Maintain a separate process manager (e.g., systemd, supervisord, or container orchestrator) to restart on failure.

## CI/CD Overview

A typical pipeline can include:

### 1) Backend build and test

- Setup Python, install deps: pip install -r backend/requirements.txt
- Run tests: pytest -q

### 2) Frontend build and E2E

- Setup Node, install deps: npm ci (in frontend/)
- Build: npm run build
- Start app for E2E (choose one):
  - Start Flask serving frontend/build: python -m backend.app &
- Run Cypress: npm run e2e:run (in frontend/) with CYPRESS_BASE_URL=http://localhost:5000

### 3) Package and deploy

- Option A: Copy the repository to the target host, install dependencies, set env vars, and start gunicorn.
- Option B: Build a container image that:
  - Installs Python dependencies
  - Builds frontend
  - Sets the working directory to NetworkWebApplication/
  - Uses gunicorn backend.wsgi:app as the entrypoint

### Example GitHub Actions sketch

- actions/checkout
- Setup Python, cache pip
- pip install -r backend/requirements.txt
- pytest -q
- Setup Node, cache npm
- npm ci (frontend/)
- npm run build (frontend/)
- Start Flask: python -m backend.app &
- Run Cypress: npm run e2e:run (frontend/)
- On success, deploy (rsync, container push, or platform-specific action)

## Troubleshooting

- Frontend shows “Frontend build not found. API is running.”: Build the frontend and ensure Flask can find frontend/build.
- API 500 on Mongo access: Ensure MONGODB_URI points to a reachable MongoDB instance and indexes can be created.
- Ping results always offline: Some environments block ICMP; manual status endpoint handles this and reports offline gracefully.

Sources: backend/app.py, backend/wsgi.py, backend/services/scheduler.py, frontend/package.json
