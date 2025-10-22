# Network Web Application

A React + Flask application for managing network devices. Users can add, view, edit, delete, and ping devices. The backend exposes RESTful APIs backed by MongoDB. The frontend is now a standalone React app; the backend serves only API endpoints.

## Overview

- Backend: Flask + Flask-RESTful in backend/
- Frontend: React in frontend/
- Production: Flask serves /api endpoints and static frontend from frontend/build
- Database: MongoDB via pymongo, configured through environment variables
- Status Monitoring: Optional ping using pythonping, with a background scheduler
- Tests: Backend (pytest: unit + integration), Frontend E2E (Cypress)

## Quickstart

### 1) Prerequisites

- Node.js 18+ and npm
- Python 3.10+ and pip
- A MongoDB instance (local or cloud) and a connection string

### 2) Clone and enter the project

- Code lives here: NetworkWebApplication/
- Frontend in NetworkWebApplication/frontend/
- Backend in NetworkWebApplication/backend/

### 3) Configure environment variables

Create a .env file in NetworkWebApplication/ (or set env vars in your shell). At minimum set MONGODB_URI. See docs/ENV.md for all variables and examples.

Example .env:
- MONGODB_URI=mongodb://localhost:27017
- MONGODB_DB=network_devices
- MONGODB_COLLECTION=devices
- APP_PORT=5000
- FLASK_DEBUG=true
- PING_ENABLED=true
- PING_INTERVAL_SECONDS=300
- PING_TIMEOUT_MS=1000

### 4) Development: run backend and frontend

- Backend (Flask API, dev mode):
  - From NetworkWebApplication/: python -m backend.app
  - Server runs on http://localhost:5000
- Frontend (React dev server):
  - From NetworkWebApplication/frontend/: npm install then npm start
  - Opens http://localhost:3000
  - The frontend is configured to proxy API requests to http://localhost:5000

### 5) Production build and serve

- Build the React app:
  - From NetworkWebApplication/frontend/: npm install && npm run build
- Start Flask with production settings and it will serve frontend/build:
  - From NetworkWebApplication/: python -m backend.app
  - Visit http://localhost:5000

See docs/DEPLOYMENT.md for options including WSGI servers.

## Project Structure

- backend/
  - app.py: Flask application factory, API registration, static serving
  - resources/: REST resources (devices CRUD, status)
  - services/: db access, ping, scheduler, validation
  - utils/: response helpers, logging config
  - models/: device_repository with CRUD
  - tests/: unit and integration tests (pytest)
- frontend/
  - src/: React UI (Dashboard, components, API client)
  - cypress/: E2E tests and config
  - package.json: scripts for dev/build/test/e2e
- docs/
  - API.md: API reference for devices and status
  - ENV.md: environment variables and examples
  - TESTING.md: how to run pytest and Cypress
  - DEPLOYMENT.md: production serving and CI/CD overview

## Common Commands

- Backend
  - pip install -r backend/requirements.txt
  - python -m backend.app  # run dev server
  - pytest -q  # run backend tests (from backend/)
- Frontend
  - npm install && npm start  # dev server on 3000
  - npm run build  # production build
  - npm run e2e:run  # run Cypress E2E (requires app running)

## Useful URLs

- API index: http://localhost:5000/api
- Health: http://localhost:5000/api/health
- Devices: http://localhost:5000/api/devices
- Frontend (dev): http://localhost:3000
- Frontend (prod via Flask): http://localhost:5000

## Documentation

- docs/API.md — endpoints and payloads
- docs/ENV.md — all environment variables
- docs/TESTING.md — backend and frontend tests
- docs/DEPLOYMENT.md — production serving, WSGI, and CI/CD

Sources: backend/app.py, backend/resources/devices.py, backend/resources/status.py, backend/config.py, frontend/package.json, backend/requirements.txt
