import React, { useMemo, useState } from 'react';
import StatusBadge from './StatusBadge';

function sortBy(arr, key, dir) {
  const mul = dir === 'desc' ? -1 : 1;
  return [...arr].sort((a, b) => {
    const va = (a[key] ?? '').toString().toLowerCase();
    const vb = (b[key] ?? '').toString().toLowerCase();
    if (va < vb) return -1 * mul;
    if (va > vb) return 1 * mul;
    return 0;
  });
}

/** DeviceTable: displays devices, with client-side sort/filter and actions */
export default function DeviceTable({
  devices = [],
  onEdit,
  onDelete,
  onPing
}) {
  const [sortKey, setSortKey] = useState('name');
  const [sortDir, setSortDir] = useState('asc');
  const [filters, setFilters] = useState({ search: '', type: '', location: '' });

  const filtered = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    const type = filters.type.trim().toLowerCase();
    const location = filters.location.trim().toLowerCase();
    let res = devices.filter(d => {
      const matchesQ =
        !q ||
        d.name?.toLowerCase().includes(q) ||
        d.ip_address?.toLowerCase().includes(q) ||
        d.location?.toLowerCase().includes(q);
      const matchesType = !type || d.device_type === type;
      const matchesLoc = !location || (d.location?.toLowerCase() === location);
      return matchesQ && matchesType && matchesLoc;
    });
    res = sortBy(res, sortKey, sortDir);
    return res;
  }, [devices, filters, sortKey, sortDir]);

  function setSort(nextKey) {
    if (sortKey === nextKey) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(nextKey);
      setSortDir('asc');
    }
  }

  return (
    <div className="table-wrapper">
      <div className="table-controls">
        <input
          placeholder="Search name, IP, location..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          aria-label="Search devices"
        />
        <select
          value={filters.type}
          onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          aria-label="Filter by device type"
        >
          <option value="">All types</option>
          <option value="router">Router</option>
          <option value="switch">Switch</option>
          <option value="server">Server</option>
          <option value="other">Other</option>
        </select>
        <input
          placeholder="Filter by location"
          value={filters.location}
          onChange={(e) => setFilters({ ...filters, location: e.target.value })}
          aria-label="Filter by location"
        />
      </div>
      <table className="devices-table">
        <thead>
          <tr>
            <th>
              <button className="linklike" onClick={() => setSort('name')} aria-label="Sort by name">
                Name {sortKey === 'name' ? (sortDir === 'asc' ? '▲' : '▼') : ''}
              </button>
            </th>
            <th>
              <button className="linklike" onClick={() => setSort('ip_address')} aria-label="Sort by IP">
                IP {sortKey === 'ip_address' ? (sortDir === 'asc' ? '▲' : '▼') : ''}
              </button>
            </th>
            <th>Type</th>
            <th>
              <button className="linklike" onClick={() => setSort('location')} aria-label="Sort by location">
                Location {sortKey === 'location' ? (sortDir === 'asc' ? '▲' : '▼') : ''}
              </button>
            </th>
            <th>Status</th>
            <th aria-label="Actions column">Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={6} style={{ textAlign: 'center', padding: '16px' }}>
                No devices found.
              </td>
            </tr>
          ) : filtered.map((d) => (
            <tr key={d.id || d._id}>
              <td>{d.name}</td>
              <td>{d.ip_address}</td>
              <td>{d.device_type}</td>
              <td>{d.location}</td>
              <td><StatusBadge status={d.status} /></td>
              <td className="actions-cell">
                <button className="btn btn-small" onClick={() => onPing?.(d)} aria-label={`Ping ${d.name}`}>Ping</button>
                <button className="btn btn-small" onClick={() => onEdit?.(d)} aria-label={`Edit ${d.name}`}>Edit</button>
                <button className="btn btn-small btn-danger" onClick={() => onDelete?.(d)} aria-label={`Delete ${d.name}`}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
