import React, { useEffect, useRef } from 'react';

/** Modal: accessible dialog wrapper */
export default function Modal({ title, children, isOpen, onClose, ariaLabelledbyId }) {
  const overlayRef = useRef(null);
  const closeBtnRef = useRef(null);

  useEffect(() => {
    function onKeyDown(e) {
      if (e.key === 'Escape') onClose?.();
    }
    if (isOpen) {
      document.addEventListener('keydown', onKeyDown);
      setTimeout(() => closeBtnRef.current?.focus(), 0);
    }
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose?.();
      }}
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby={ariaLabelledbyId || 'modal-title'}
    >
      <div
        style={{
          background: '#fff',
          color: '#111',
          minWidth: '320px',
          maxWidth: '90vw',
          width: '600px',
          borderRadius: 10,
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
          padding: '16px'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 id={ariaLabelledbyId || 'modal-title'} style={{ margin: 0, fontSize: '1.25rem' }}>
            {title}
          </h2>
          <button
            ref={closeBtnRef}
            onClick={onClose}
            aria-label="Close dialog"
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '1.25rem',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
        <div style={{ marginTop: 12 }}>{children}</div>
      </div>
    </div>
  );
}
