import React from 'react';

/** Notifications: renders a list of alert messages */
export default function Notifications({ notifications = [], onDismiss }) {
  if (!notifications.length) return null;
  return (
    <div aria-live="polite" aria-atomic="true" style={{ marginBottom: '1rem' }}>
      {notifications.map((n) => (
        <div
          key={n.id}
          role={n.type === 'error' ? 'alert' : 'status'}
          style={{
            padding: '10px 12px',
            borderRadius: 8,
            marginBottom: 8,
            border: '1px solid',
            backgroundColor: n.type === 'error' ? '#fff5f5' : '#f0fff4',
            color: n.type === 'error' ? '#721c24' : '#155724',
            borderColor: n.type === 'error' ? '#f5c6cb' : '#c3e6cb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{n.message}</span>
          {onDismiss && (
            <button
              onClick={() => onDismiss(n.id)}
              aria-label="Dismiss notification"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'inherit',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
            >
              ×
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
