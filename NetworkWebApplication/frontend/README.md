# Frontend (React)

This frontend is a standalone React application. It does not assume Flask serves static assets.

- Development:
  - From this directory: `npm install` then `npm start` (runs on http://localhost:3000).
  - Point to the backend API by setting `REACT_APP_API_BASE` (e.g., `http://localhost:5000/api`).
  - You can create `.env.development.local` with:
    REACT_APP_API_BASE=http://localhost:5000/api
- Production:
  - `npm run build` produces a static build under `build/` which you can serve with any static host (NGINX, S3, etc.).
  - Ensure `REACT_APP_API_BASE` is set at build time to the correct API URL for your environment.
- API Base:
  - The client reads `process.env.REACT_APP_API_BASE`, defaulting to `/api` if not set.
  - Example:
    - Local dev with separate backend: `REACT_APP_API_BASE=http://localhost:5000/api`
    - Same-origin reverse proxy: `/api` (default)

Notes:
- For local development you may keep a `proxy` field in package.json to simplify CORS during dev; otherwise rely on `REACT_APP_API_BASE`.
