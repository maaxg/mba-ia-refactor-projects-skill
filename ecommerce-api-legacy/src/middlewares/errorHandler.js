'use strict';

/** Domain error mapped to HTTP 400 by the centralized handler. */
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.status = 400;
  }
}

/**
 * Centralized error handler — replaces the legacy swallowed errors and ad-hoc
 * res.status(500).send("Erro DB"). Logs 500s server-side; clients get safe messages.
 */
function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
  const status = err.status || 500;
  if (status >= 500) {
    console.error('Unhandled error:', err);
  }
  res.status(status).json({ error: status >= 500 ? 'Erro interno do servidor' : err.message });
}

module.exports = { errorHandler, ValidationError };
