const { defineConfig } = require('cypress');

const DEFAULT_BASE_URL =
  process.env.CYPRESS_BASE_URL ||
  process.env.REACT_APP_SITE_URL ||
  process.env.REACT_APP_BASE_URL ||
  // Default to Flask-served frontend build; dev fallback to CRA port if needed via scripts
  'http://localhost:5000';

module.exports = defineConfig({
  e2e: {
    baseUrl: DEFAULT_BASE_URL,
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    video: false,
    viewportWidth: 1280,
    viewportHeight: 800,
    retries: {
      runMode: 1,
      openMode: 0
    },
    defaultCommandTimeout: 8000
  },
  env: {
    apiBase: process.env.CYPRESS_API_BASE || '/api'
  }
});
