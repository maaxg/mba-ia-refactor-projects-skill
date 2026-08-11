'use strict';

const settings = require('../config/settings');

/**
 * Authorization guard for admin/destructive endpoints (the legacy versions were public).
 * Requires an X-Admin-Token header matching settings.adminToken (from the environment).
 */
function requireAdmin(req, res, next) {
  const token = req.headers['x-admin-token'];
  if (!token || token !== settings.adminToken) {
    return res.status(401).json({ error: 'Acesso administrativo negado' });
  }
  return next();
}

module.exports = requireAdmin;
