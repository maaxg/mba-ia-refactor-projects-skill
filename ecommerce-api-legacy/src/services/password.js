'use strict';

const crypto = require('crypto');

/**
 * Proper password hashing using Node's built-in scrypt (salted, no extra dependency).
 * Replaces the legacy `badCrypto` base64 "hash". Stored format: "<salt>:<derivedKey>".
 */
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const derived = crypto.scryptSync(String(password), salt, 64).toString('hex');
  return `${salt}:${derived}`;
}

function verifyPassword(password, stored) {
  if (typeof stored !== 'string' || !stored.includes(':')) return false;
  const [salt, key] = stored.split(':');
  const derived = crypto.scryptSync(String(password), salt, 64).toString('hex');
  const keyBuf = Buffer.from(key, 'hex');
  const derivedBuf = Buffer.from(derived, 'hex');
  return keyBuf.length === derivedBuf.length && crypto.timingSafeEqual(keyBuf, derivedBuf);
}

module.exports = { hashPassword, verifyPassword };
