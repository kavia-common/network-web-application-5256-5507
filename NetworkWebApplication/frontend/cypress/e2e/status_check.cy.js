/**
 * Manual Status Check E2E:
 * - Create a device entry
 * - Trigger Ping action
 * - Expect a success or error notification and badge remains visible
 * - Clean up by deleting the device
 *
 * Note: Actual ICMP ping may be blocked in CI environments; backend reports offline gracefully.
 */

const uniqueSuffix = Date.now();
const device = {
  name: `Ping Target ${uniqueSuffix}`,
  ip_address: `192.0.2.${(uniqueSuffix % 200) || 10}`, // TEST-NET-1 range; expected offline
  device_type: 'router',
  location: 'TestNet',
  status: ''
};

describe('Manual status check (Ping)', () => {
  before(() => {
    cy.apiDeleteByIP(device.ip_address);
  });

  it('should add device to ping', () => {
    cy.visit('/');
    cy.openAddDeviceModal();
    cy.fillDeviceForm(device);
    cy.submitDeviceForm();

    cy.contains('td', device.name).should('be.visible');
  });

  it('should trigger ping and show feedback notification', () => {
    cy.findDeviceRowByName(device.name).within(() => {
      cy.contains('button', /^ping$/i).click();
    });

    // Expect notification either "Ping success" or "Ping failed"
    cy.contains(/ping (success|failed)/i, { timeout: 15000 }).should('be.visible');

    // Status badge should be present
    cy.findDeviceRowByName(device.name).within(() => {
      cy.findByRole('status').should('exist');
    });
  });

  it('cleanup: delete ping test device', () => {
    cy.findDeviceRowByName(device.name).within(() => {
      cy.contains('button', /delete/i).click();
    });
    cy.confirmDeletion();
    cy.contains('td', device.name).should('not.exist');
  });
});
