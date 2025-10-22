import React from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';

// PUBLIC_INTERFACE
export default function App() {
  /** App shell renders Dashboard; routing can be added later if needed. */
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}
