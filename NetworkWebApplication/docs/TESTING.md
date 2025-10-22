# Testing

This project includes backend unit/integration tests (pytest) and frontend end-to-end tests (Cypress).

## Backend Tests (pytest)

### Structure

- backend/tests/unit/: unit tests for services, models, and utils
- backend/tests/integration/: API endpoint tests using Flask test client and mongomock

pytest.ini sets:
- addopts = -q
- testpaths = backend/tests

### Running

From NetworkWebApplication/backend/:

- python -m pip install -r requirements.txt
- pytest -q

Notes:
- Integration tests monkeypatch backend.services.db.get_collection to use mongomock, avoiding real Mongo connections.
- Scheduler is disabled in tests via PING_ENABLED=false.
- Some tests patch pythonping.ping to simulate online/offline responses.

## Frontend E2E Tests (Cypress)

### Requirements

- Backend running and serving API at http://localhost:5000 (dev or prod)
- Frontend served either by React dev server (3000) or by Flask (5000) if built

Cypress baseUrl is determined by frontend/cypress.config.js:
- CYPRESS_BASE_URL or REACT_APP_SITE_URL or REACT_APP_BASE_URL, otherwise defaults to http://localhost:5000
- API base for cy.request is env apiBase defaulting to /api

### Commands

From NetworkWebApplication/frontend/:

- npm install
- To open Cypress UI:
  - npm run e2e:open
- To run headless:
  - npm run e2e:run

Suggested setups:
- Dev mode: run Flask backend (5000) and React dev server (3000), then CYPRESS_BASE_URL=http://localhost:3000 npm run e2e:run
- Prod mode: build frontend (npm run build), run Flask (serves frontend) and then npm run e2e:run (defaults to 5000)

### Test Coverage

E2E specs include:
- devices_crud.cy.js: add, edit, delete flow with UI assertions
- status_check.cy.js: manual ping flow and cleanup

### Troubleshooting

- If pinging requires privileges, backend uses pythonping with privileged=False and handles failures by reporting offline.
- Ensure MONGODB_URI is configured for real runs; for ephemeral test runs, Cypress tests can pass without DB persistence if API endpoints are operational and connected to Mongo.
- If Cypress cannot find @testing-library/cypress, support file gracefully skips those commands.

## CI Integration

- Suggested pipeline:
  - Install backend deps and run pytest
  - Install frontend deps, build frontend
  - Start backend (serving built frontend) on a CI port
  - Run Cypress headless against the started app
  - Collect test artifacts (optional)

See docs/DEPLOYMENT.md for a CI/CD overview.

Sources: backend/pytest.ini, backend/tests/*, frontend/cypress.config.js, frontend/package.json
