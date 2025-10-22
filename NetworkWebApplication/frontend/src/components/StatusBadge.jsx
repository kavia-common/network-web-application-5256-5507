import React from 'react';

/** StatusBadge: small colored indicator for device status */
export default function StatusBadge({ status }) {
  const s = (status || 'unknown').toLowerCase();
  const colorMap = {
    online: '#28a745',
    offline: '#dc3545',
    unknown: '#6c757d'
  };
  const labelMap = {
    online: 'Online',
    offline: 'Offline',
    unknown: 'Unknown'
  };
  const color = colorMap[s] || colorMap.unknown;
  const label = labelMap[s] || labelMap.unknown;

  return (
    <span
      role="status"
      aria-label={`Status: ${label}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '2px 8px',
        borderRadius: '12px',
        backgroundColor: '#f1f3f5',
        color: '#212529',
        fontSize: '0.85rem',
        border: '1px solid rgba(0,0,0,0.05)'
      }}
    >
      <span
        aria-hidden="true"
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: color,
          display: 'inline-block'
        }}
      />
      {label}
    </span>
  );
}
