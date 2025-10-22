/**
 * Devices CRUD E2E flow:
 * - Open dashboard
 * - Create a device
 * - Edit the device
 * - Delete the device with confirmation
 * Assertions verify visible feedback and table updates.
 */

const uniqueSuffix = Date.now();

const device = {
  name: `Test Device ${uniqueSuffix}`,
  ip_address: `192.168.${Math.floor(uniqueSuffix % 200)}.${uniqueSuffix % 200}`,
  device_type: 'server',
  location: 'Lab',
  status: ''
};

const edited = {
  name: `Edited Device ${uniqueSuffix}`,
  location: 'Lab-2'
};

describe('Devices CRUD', () => {
  before(() => {
    // Best-effort cleanup of any lingering device with same IP
    cy.apiDeleteByIP(device.ip_address);
  });

  it('should load dashboard', () => {
    cy.visit('/');
    cy.contains(/network devices/i).should('be.visible');
    cy.contains('button', /add device/i).should('be.visible');
  });

  it('should create a device and show success notification', () => {
    cy.openAddDeviceModal();
    cy.fillDeviceForm(device);
    cy.submitDeviceForm();

    // Table should include the new device
    cy.contains('td', device.name).should('be.visible');
    cy.contains('td', device.ip_address).should('be.visible');

    // Success notification (aria role status)
    cy.contains(/device created successfully/i).should('be.visible');
  });

  it('should edit the created device and reflect changes', () => {
    cy.findDeviceRowByName(device.name).within(() => {
      cy.contains('button', /edit/i).click();
    });

    cy.findByRole('dialog').should('be.visible');
    cy.fillDeviceForm({ name: edited.name, location: edited.location });
    cy.submitDeviceForm();

    cy.contains('td', edited.name).should('be.visible');
    cy.contains(/device updated successfully/i).should('be.visible');
  });

  it('should delete the device after confirmation', () => {
    cy.findDeviceRowByName(edited.name).within(() => {
      cy.contains('button', /delete/i).click();
    });

    cy.findByRole('dialog').within(() => {
      cy.contains(/are you sure/i).should('be.visible');
    });

    cy.confirmDeletion();

    cy.contains('td', edited.name).should('not.exist');
    cy.contains(/device deleted/i).should('be.visible');
  });
});
