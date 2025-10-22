/**
 * API base URL is configurable via environment:
 * - REACT_APP_API_BASE: full base such as "http://localhost:5000/api" or just "/api"
 * Defaults to "/api" to support local proxy or same-origin deployments.
 */
const BASE_URL = process.env.REACT_APP_API_BASE || '/api';

// PUBLIC_INTERFACE
export async function apiRequest(path, { method = 'GET', headers = {}, body } = {}) {
  /** Simple fetch wrapper that prefixes BASE_URL, handles JSON, and throws on HTTP errors. */
  const url = `${BASE_URL}${path}`;
  const opts = {
    method,
    headers: {
      Accept: 'application/json',
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  };

  let res;
  try {
    res = await fetch(url, opts);
  } catch (networkErr) {
    const err = new Error('Network error. Please check your connection.');
    err.cause = networkErr;
    err.isNetworkError = true;
    throw err;
  }

  let data;
  const isJson = res.headers.get('content-type')?.includes('application/json');
  if (isJson) {
    try {
      data = await res.json();
    } catch {
      data = null;
    }
  } else {
    data = await res.text().catch(() => null);
  }

  if (!res.ok) {
    const message = (data && data.message) || `Request failed with status ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  // Standard backend success shape: { status, message, data }
  if (data && typeof data === 'object' && 'data' in data) {
    return data.data;
  }
  return data;
}
