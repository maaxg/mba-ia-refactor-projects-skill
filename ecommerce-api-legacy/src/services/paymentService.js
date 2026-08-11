'use strict';

/**
 * Payment service — isolates the (simulated) gateway charge from the checkout flow.
 *
 * NOTE: this is a SIMULATION; real gateway integration is out of scope. Unlike the legacy
 * code it never logs the card number (PAN) or the gateway secret key.
 */
function charge(card, amount) {
  const approved = typeof card === 'string' && card.startsWith('4');
  return { status: approved ? 'PAID' : 'DENIED', amount };
}

module.exports = { charge };
