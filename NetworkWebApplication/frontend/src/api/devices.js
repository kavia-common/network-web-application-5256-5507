import { apiRequest } from './client';

// PUBLIC_INTERFACE
export async function getDevices(filters = {}) {
  /** Fetch list of devices with optional filters */
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v).trim() !== '') {
      params.append(k, v);
    }
  });
  const qs = params.toString();
  return apiRequest(`/devices${qs ? `?${qs}` : ''}`);
}

// PUBLIC_INTERFACE
export async function createDevice(device) {
  /** Create a new device */
  return apiRequest('/devices', { method: 'POST', body: device });
}

// PUBLIC_INTERFACE
export async function updateDevice(id, updates, method = 'PATCH') {
  /** Update an existing device by id */
  return apiRequest(`/devices/${encodeURIComponent(id)}`, { method, body: updates });
}

// PUBLIC_INTERFACE
export async function deleteDevice(id) {
  /** Delete a device by id */
  // For 204, apiRequest would try to parse; handle here via fetch
  const BASE_URL = process.env.REACT_APP_API_BASE || '/api';
  const res = await fetch(`${BASE_URL}/devices/${encodeURIComponent(id)}`, {
    method: 'DELETE',
    headers: { 'Accept': 'application/json' }
  });
  if (!res.ok && res.status !== 204) {
    let data = null;
    try {
      data = await res.json();
    } catch {
      // noop
    }
    const message = (data && data.message) || `Request failed with status ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return true;
}

// PUBLIC_INTERFACE
export async function getDeviceStatus(id) {
  /** Manually ping a device and return updated info and ping result */
  return apiRequest(`/devices/${encodeURIComponent(id)}/status`);
}
