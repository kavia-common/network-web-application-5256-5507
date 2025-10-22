import React, { useEffect, useMemo, useState } from 'react';
import Notifications from '../components/Notifications';
import Modal from '../components/Modal';
import DeviceForm from '../components/DeviceForm';
import DeviceTable from '../components/DeviceTable';
import { getDevices, createDevice, updateDevice, deleteDevice, getDeviceStatus } from '../api/devices';

let notifIdCounter = 1;

export default function Dashboard() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notif, setNotif] = useState([]);
  const [isFormOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  function addNotif(type, message) {
    const id = notifIdCounter++;
    setNotif((prev) => [...prev, { id, type, message }]);
    // auto dismiss after 4s for success, keep error until closed
    if (type !== 'error') {
      setTimeout(() => {
        setNotif((prev) => prev.filter((n) => n.id !== id));
      }, 4000);
    }
  }

  function dismissNotif(id) {
    setNotif((prev) => prev.filter((n) => n.id !== id));
  }

  async function load() {
    setLoading(true);
    try {
      const list = await getDevices();
      setDevices(list || []);
    } catch (e) {
      addNotif('error', e.message || 'Failed to load devices');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function openCreate() {
    setEditing(null);
    setFormOpen(true);
  }

  function openEdit(d) {
    setEditing(d);
    setFormOpen(true);
  }

  async function handleSave(formValues) {
    setSubmitting(true);
    try {
      if (editing) {
        const updated = await updateDevice(editing.id, formValues, 'PATCH');
        setDevices((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
        addNotif('success', 'Device updated successfully');
      } else {
        const created = await createDevice(formValues);
        setDevices((prev) => [created, ...prev]);
        addNotif('success', 'Device created successfully');
      }
      setFormOpen(false);
      setEditing(null);
    } catch (e) {
      const apiCode = e?.data?.code;
      if (apiCode === 'DUPLICATE_IP') {
        addNotif('error', 'A device with this IP address already exists.');
      } else if (apiCode === 'VALIDATION_ERROR') {
        addNotif('error', e.message || 'Validation error');
      } else {
        addNotif('error', e.message || 'Failed to save device');
      }
    } finally {
      setSubmitting(false);
    }
  }

  function askDelete(d) {
    setConfirmDelete(d);
  }

  async function confirmDeleteAction() {
    const d = confirmDelete;
    if (!d) return;
    try {
      await deleteDevice(d.id);
      setDevices((prev) => prev.filter((x) => x.id !== d.id));
      addNotif('success', 'Device deleted');
    } catch (e) {
      addNotif('error', e.message || 'Failed to delete device');
    } finally {
      setConfirmDelete(null);
    }
  }

  async function pingDevice(d) {
    try {
      const result = await getDeviceStatus(d.id);
      const updated = result?.device || null;
      if (updated) {
        setDevices((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));
      }
      const ping = result?.ping;
      if (ping) {
        const msg =
          ping.status === 'online'
            ? `Ping success: ${ping.latency_ms ?? 'N/A'} ms`
            : 'Ping failed: device offline';
        addNotif(ping.status === 'online' ? 'success' : 'error', msg);
      } else {
        addNotif('success', 'Status checked');
      }
    } catch (e) {
      addNotif('error', e.message || 'Failed to check status');
    }
  }

  const body = useMemo(() => {
    if (loading) {
      return <div className="loading">Loading devices...</div>;
    }
    return (
      <>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={openCreate}>Add Device</button>
        </div>
        <DeviceTable
          devices={devices}
          onEdit={openEdit}
          onDelete={askDelete}
          onPing={pingDevice}
        />
      </>
    );
  }, [loading, devices]);

  return (
    <div className="container">
      <header className="navbar">
        <h1 className="title">Network Devices</h1>
      </header>

      <main>
        <Notifications notifications={notif} onDismiss={dismissNotif} />
        {body}
      </main>

      <Modal
        title={editing ? 'Edit Device' : 'Add Device'}
        isOpen={isFormOpen}
        onClose={() => { setFormOpen(false); setEditing(null); }}
      >
        <DeviceForm initialValues={editing || undefined} onSubmit={handleSave} submitting={submitting} />
      </Modal>

      <Modal
        title="Confirm Deletion"
        isOpen={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
      >
        <p>Are you sure you want to delete device <strong>{confirmDelete?.name}</strong>?</p>
        <div className="form-actions">
          <button className="btn btn-danger" onClick={confirmDeleteAction}>Delete</button>
          <button className="btn" onClick={() => setConfirmDelete(null)}>Cancel</button>
        </div>
      </Modal>
    </div>
  );
}
