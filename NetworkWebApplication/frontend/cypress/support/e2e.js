/**
 * Cypress global support file.
 * Adds custom commands to interact with the UI for CRUD and ping flows.
 */

// Selectors used across tests
Cypress.Commands.add('openAddDeviceModal', () => {
  cy.contains('button', /add device/i).click();
  cy.findByRole('dialog').should('exist');
});

Cypress.Commands.add('fillDeviceForm', (device) => {
  if (device.name !== undefined) cy.get('input[name="name"]').clear().type(device.name);
  if (device.ip_address !== undefined) cy.get('input[name="ip_address"]').clear().type(device.ip_address);
  if (device.device_type !== undefined) cy.get('select[name="device_type"]').select(device.device_type);
  if (device.location !== undefined) cy.get('input[name="location"]').clear().type(device.location);
  if (device.status !== undefined) cy.get('select[name="status"]').select(device.status || '');
});

Cypress.Commands.add('submitDeviceForm', () => {
  cy.contains('button', /^save$/i).click();
});

// Delete confirm modal helpers
Cypress.Commands.add('confirmDeletion', () => {
  cy.findByRole('dialog').within(() => {
    cy.contains('button', /delete/i).click();
  });
});

// Ensure notifications appear with message text
Cypress.Commands.add('expectNotification', (matcher) => {
  cy.findAllByRole(/alert|status/).contains(matcher).should('be.visible');
});

// Utility to find a row by device name
Cypress.Commands.add('findDeviceRowByName', (name) => {
  return cy.contains('td', name).parents('tr');
});

// Clean up helper via API if available (best-effort)
Cypress.Commands.add('apiDeleteByIP', (ip) => {
  const apiBase = Cypress.env('apiBase') || '/api';
  cy.request('GET', `${apiBase}/devices`).then((res) => {
    const devices = (res.body && res.body.data) || [];
    const target = devices.find((d) => d.ip_address === ip);
    if (target && target.id) {
      cy.request('DELETE', `${apiBase}/devices/${target.id}`);
    }
  });
});

// Include @testing-library/cypress for accessible queries
// This is optional if the dependency is available; otherwise simple selectors are used.
// We guard require() to avoid runtime errors if not installed in certain environments.
try {
  require('@testing-library/cypress/add-commands');
} catch (e) {
  // no-op; tests fall back to cy.contains and cy.get selectors
}
