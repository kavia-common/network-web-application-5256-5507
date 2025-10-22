# Deployment and CI/CD

This document explains how to serve the application in production and outlines a CI/CD approach.

## Production Serving

In production, the backend (Flask) serves only the REST API under /api. The React frontend is built and served independently (e.g., NGINX, CDN, or static hosting).

### Build frontend

From NetworkWebApplication/frontend/:

- npm install
- REACT_APP_API_BASE=https://your-backend.example.com/api npm run build

This generates frontend/build to deploy to your static hosting solution.

### Run Flask in production

From NetworkWebApplication/:

- Ensure environment variables are set (see docs/ENV.md). At minimum: MONGODB_URI.
- Start the API:
  - python -m backend.app
- Or with gunicorn:
  - gunicorn -w 3 -b 0.0.0.0:${APP_PORT:-5000} backend.wsgi:app

The API listens on APP_PORT (default 5000). Health: http://localhost:5000/api/health

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

Frontend build-time env:
- REACT_APP_API_BASE: API base URL used by the frontend (e.g., https://api.example.com/api)

## Background Scheduler

- Controlled by PING_ENABLED. When true, the app starts a background job to ping all devices at PING_INTERVAL_SECONDS and update status/last_ping.
- If Mongo is not configured, ensure PING_ENABLED=false or set the database variables before starting.

## Zero-Downtime Considerations

- Build the frontend ahead of time and deploy to a static host with caching.
- Start the WSGI server with multiple workers.
- Maintain a separate process manager or orchestrator to restart on failure.

## CI/CD Overview

A typical pipeline can include:

### 1) Backend build and test

- Setup Python, install deps: pip install -r backend/requirements.txt
- Run tests: pytest -q

### 2) Frontend build and E2E

- Setup Node, install deps: npm ci (in frontend/)
- Build: REACT_APP_API_BASE=$PROD_API_BASE npm run build
- Start backend API on CI for E2E (port 5000), and run frontend served by dev server (port 3000) or serve the built assets with a static server (e.g., serve) for tests.
- Run Cypress:
  - Dev server: CYPRESS_BASE_URL=http://localhost:3000 npm run e2e:run (frontend/)
  - Static build: CYPRESS_BASE_URL=http://localhost:5000 (if you reverse-proxy static separately)

### 3) Package and deploy

- Option A: Deploy backend and frontend separately (API service + static hosting).
- Option B: Containerize both as separate images and deploy with your orchestrator.

### Example GitHub Actions sketch

- actions/checkout
- Setup Python, cache pip
- pip install -r backend/requirements.txt
- pytest -q
- Setup Node, cache npm
- npm ci (frontend/)
- REACT_APP_API_BASE=$API_BASE npm run build (frontend/)
- Start Flask API: python -m backend.app &
- Run Cypress against http://localhost:3000 or serve build and test accordingly
- On success, deploy artifacts

## Troubleshooting

- Frontend 404/API errors: verify REACT_APP_API_BASE is set correctly to your backend’s /api base.
- API 500 on Mongo access: Ensure MONGODB_URI points to a reachable MongoDB instance and indexes can be created.
- Ping results always offline: Some environments block ICMP; manual status endpoint handles this and reports offline gracefully.

Sources: backend/app.py, backend/wsgi.py, backend/services/scheduler.py, frontend/package.json
