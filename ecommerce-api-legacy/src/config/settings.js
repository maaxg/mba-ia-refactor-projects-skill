'use strict';

/**
 * Application configuration — sourced from environment variables.
 * No secrets are hardcoded here (the legacy utils.js embedded live DB/payment keys).
 */
module.exports = {
  port: parseInt(process.env.PORT || '3000', 10),
  // DB path is configurable; ':memory:' keeps the original zero-config behavior,
  // set DB_PATH=./lms.db (or similar) for persistence.
  dbPath: process.env.DB_PATH || ':memory:',
  adminToken: process.env.ADMIN_TOKEN || 'dev-admin-token-change-me',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  corsOrigins: (process.env.CORS_ORIGINS || 'http://localhost:3000').split(','),
};
