import React, { useState, useEffect } from 'react';

const defaultValues = {
  name: '',
  ip_address: '',
  device_type: 'router',
  location: '',
  status: ''
};

/** DeviceForm: for create and edit device */
export default function DeviceForm({ initialValues, onSubmit, submitting = false }) {
  const [values, setValues] = useState({ ...defaultValues, ...(initialValues || {}) });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setValues({ ...defaultValues, ...(initialValues || {}) });
    setErrors({});
  }, [initialValues]);

  function handleChange(e) {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const e = {};
    if (!values.name.trim()) e.name = 'Name is required.';
    if (!values.ip_address.trim()) e.ip_address = 'IP address is required.';
    if (!values.device_type.trim()) e.device_type = 'Device type is required.';
    if (!values.location.trim()) e.location = 'Location is required.';
    return e;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const eMap = validate();
    setErrors(eMap);
    if (Object.keys(eMap).length) return;
    await onSubmit?.(values);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-grid">
        <label>
          <span>Name</span>
          <input
            name="name"
            value={values.name}
            onChange={handleChange}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? 'err-name' : undefined}
          />
          {errors.name && <span id="err-name" className="error-text">{errors.name}</span>}
        </label>

        <label>
          <span>IP Address</span>
          <input
            name="ip_address"
            value={values.ip_address}
            onChange={handleChange}
            aria-invalid={!!errors.ip_address}
            aria-describedby={errors.ip_address ? 'err-ip' : undefined}
            placeholder="e.g., 192.168.1.10"
          />
          {errors.ip_address && <span id="err-ip" className="error-text">{errors.ip_address}</span>}
        </label>

        <label>
          <span>Device Type</span>
          <select
            name="device_type"
            value={values.device_type}
            onChange={handleChange}
            aria-invalid={!!errors.device_type}
            aria-describedby={errors.device_type ? 'err-type' : undefined}
          >
            <option value="router">Router</option>
            <option value="switch">Switch</option>
            <option value="server">Server</option>
            <option value="other">Other</option>
          </select>
          {errors.device_type && <span id="err-type" className="error-text">{errors.device_type}</span>}
        </label>

        <label>
          <span>Location</span>
          <input
            name="location"
            value={values.location}
            onChange={handleChange}
            aria-invalid={!!errors.location}
            aria-describedby={errors.location ? 'err-location' : undefined}
            placeholder="e.g., Data Center A"
          />
          {errors.location && <span id="err-location" className="error-text">{errors.location}</span>}
        </label>

        <label>
          <span>Status (optional)</span>
          <select name="status" value={values.status || ''} onChange={handleChange}>
            <option value="">(Not set)</option>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn" disabled={submitting}>
          {submitting ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
}
