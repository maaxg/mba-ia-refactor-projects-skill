'use strict';

const express = require('express');

const requireAdmin = require('../middlewares/auth');

/**
 * Routing layer (Views) — maps URL + method → controller. No logic, no DB.
 * Same endpoints as the legacy app; admin/destructive routes are now guarded.
 */
function buildRouter({ checkoutController, reportController, userController }) {
  const router = express.Router();

  router.post('/api/checkout', checkoutController.checkout);
  router.get('/api/admin/financial-report', requireAdmin, reportController.financialReport);
  router.delete('/api/users/:id', requireAdmin, userController.deleteUser);

  return router;
}

module.exports = buildRouter;
