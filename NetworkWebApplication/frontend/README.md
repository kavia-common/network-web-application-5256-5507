# Frontend (React)

- Development: `npm start` from this directory. Dev server proxies API to http://localhost:5000 via `proxy` in package.json.
- Production: `npm run build` and Flask serves `frontend/build` at runtime.
- API base: The client uses `process.env.REACT_APP_API_BASE` when set, otherwise defaults to `/api` (behind Flask). Set `REACT_APP_API_BASE` if your API is on a different origin/path.
