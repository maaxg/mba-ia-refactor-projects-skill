```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.x (^4.18.2, resolved 4.22.x)
Dependencies:  sqlite3 ^5.1.6
Domain:        LMS / e-commerce checkout ("Frankenstein LMS") —
               users, courses, enrollments, payments, audit_logs
Architecture:  God class — AppManager owns DB connection, schema, seeding, routing,
               validation, payment logic and reporting in one file
Source files:  3 files analyzed (~185 lines)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite in-memory)
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.x
Files:   3 analyzed | ~185 lines of code
Date:    2026-08-11

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 3 | LOW: 3
Total: 16 findings

## Findings

### [CRITICAL] Hardcoded production secrets & payment key (AP-01)
- **File:** `src/utils.js:2-5`
- **Description:** `dbUser`, `dbPass ("senha_super_secreta_prod_123")`, `paymentGatewayKey ("pk_live_1234567890abcdef")` and `smtpUser` are hardcoded literals.
- **Impact:** Live payment-gateway and DB credentials leaked in source/git history; unrotatable.
- **Recommendation:** Move all to env-based `config/settings.js`. Playbook RP-01.

### [CRITICAL] Full card number + gateway key written to logs (AP-01/AP-17)
- **File:** `src/AppManager.js:45`
- **Description:** `console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)` logs the raw PAN and the secret key on every checkout.
- **Impact:** PCI-DSS violation and secret leakage to stdout/log aggregation.
- **Recommendation:** Never log PANs/secrets; move charging to a payment service that logs only a masked reference. Playbook RP-12.

### [CRITICAL] Broken password hashing + plaintext seed (AP-05)
- **File:** `src/utils.js:17-23` (`badCrypto`), used at `src/AppManager.js:68`; plaintext seed at `src/AppManager.js:18`
- **Description:** `badCrypto` base64-encodes (not hashes), loops uselessly 10 000×, and truncates to 10 chars — no salt, reversible; the seed user is stored with pass `'123'` in clear text.
- **Impact:** Passwords trivially recoverable on any DB leak.
- **Recommendation:** Real hashing (bcrypt or Node `crypto.scrypt` with salt); hash the seed. Playbook RP-05.

### [CRITICAL] Fake payment authorization (AP-04)
- **File:** `src/AppManager.js:46`
- **Description:** Payment "approval" is `cc.startsWith("4") ? "PAID" : "DENIED"` — no gateway call; any Visa-like number is accepted.
- **Impact:** Enrollments/payments recorded as PAID with no real charge; trivially bypassable.
- **Recommendation:** Isolate in a payment service behind a real gateway interface (simulation documented as out-of-scope). Playbook RP-04/RP-06.

### [CRITICAL] No authentication on admin/destructive endpoints (AP-09)
- **File:** `src/AppManager.js:80` (`GET /api/admin/financial-report`), `src/AppManager.js:131` (`DELETE /api/users/:id`)
- **Description:** The financial report and the user-delete are fully public — no auth/authorization.
- **Impact:** Anyone can read revenue/PII or delete users.
- **Recommendation:** `requireAdmin` middleware (token/role). Playbook RP-06.

### [HIGH] God class: AppManager does everything (AP-03)
- **File:** `src/AppManager.js:4-141`
- **Description:** One class owns the DB connection (`:7`), schema+seed (`initDb` 10-23), routing, validation, payment logic and reporting.
- **Impact:** Untestable in isolation; every change risks unrelated behavior.
- **Recommendation:** Split into config/db, per-entity models, controllers, routes, services. Playbook RP-03.

### [HIGH] Business logic inline in the route handler (AP-07)
- **File:** `src/AppManager.js:28-78`
- **Description:** The entire checkout workflow (find course, find/create user, charge, enroll, record payment, audit) is nested inside the route callback.
- **Impact:** No reuse, no unit testing, violates MVC/SRP.
- **Recommendation:** Thin route → `checkoutController` → models/services. Playbook RP-04.

### [HIGH] Non-atomic checkout, no transaction (AP-10)
- **File:** `src/AppManager.js:50, 54, 57`
- **Description:** Enrollment, payment and audit-log inserts are separate writes with no transaction; a mid-flow failure leaves orphaned rows.
- **Impact:** Data corruption (enrollment without payment, etc.).
- **Recommendation:** Wrap the flow in BEGIN/COMMIT with ROLLBACK on error. Playbook RP-07.

### [HIGH] N+1 query explosion in financial report (AP-11)
- **File:** `src/AppManager.js:83 → 92 → 104 → 106`
- **Description:** Loops courses → per-course enrollments → per-enrollment user + payment queries; revenue summed in app code. Also hand-rolled `coursesPending`/`enrPending` counters for async coordination (`:86-98, 117-122`) — race-prone.
- **Impact:** O(courses·enrollments) round-trips; fragile concurrency.
- **Recommendation:** Single JOIN + `SUM()` aggregate; async/await instead of manual counters. Playbook RP-08.

### [HIGH] Orphaned data on delete + swallowed error (AP-08/AP-15)
- **File:** `src/AppManager.js:131-137`
- **Description:** `DELETE /api/users/:id` removes the user but leaves enrollments/payments dangling (the response text at `:135` literally admits it); the `err` at `:133` is ignored.
- **Impact:** Referential garbage; silent failures.
- **Recommendation:** Cascade-delete dependent rows in a transaction; handle errors. Playbook RP-07.

### [MEDIUM] Weak / missing input validation (AP-13)
- **File:** `src/AppManager.js:35`
- **Description:** Checks only `u,e,cid,cc` (password `p` unchecked); no email/card-format validation; cryptic body keys (`usr,eml,pwd,c_id,card`).
- **Impact:** Bad data, weak default password path (`"123456"` at `:68`).
- **Recommendation:** Validate all fields at the boundary. Playbook RP-11.

### [MEDIUM] Swallowed errors in nested callbacks (AP-15)
- **File:** `src/AppManager.js:104, 106, 133`
- **Description:** DB `err` is ignored in the report user/payment lookups and in the delete callback, so failures silently corrupt results/response.
- **Impact:** Hidden bugs, wrong reports, false "success".
- **Recommendation:** Centralized error middleware; `try/catch` around awaited queries. Playbook RP-10.

### [MEDIUM] Deprecated/legacy patterns: callback-style sqlite3 + in-memory data loss (AP-12)
- **File:** callback pyramid `src/AppManager.js:37-77, 83-128`; in-memory DB `src/AppManager.js:7` (`:memory:`)
- **Description:** Uses the legacy callback-based sqlite3 API (no promise wrapper) throughout, and an in-memory database that loses all data on every restart.
- **Impact:** Callback hell, unhandled rejections, non-persistence.
- **Recommendation:** Promisify the driver and use async/await; make the DB path configurable/persistent. Playbook RP-09.

### [LOW] Magic numbers / strings (AP-16)
- **File:** `src/utils.js:6` (port 3000), `src/utils.js:19-22` (10000, base64 substrings), `src/AppManager.js:46` (`"4"`), `src/AppManager.js:68` (`"123456"`)
- **Description:** Unnamed literals for config and logic.
- **Recommendation:** Named constants / config. Playbook RP-12.

### [LOW] Global mutable state & stale export (AP-08/AP-18)
- **File:** `src/utils.js:9-10` (`globalCache`, `totalRevenue`), exported at `:25`, imported unused at `src/AppManager.js:2`
- **Description:** Module-level mutable globals; `totalRevenue` is exported by value, never updated, and imported but unused.
- **Impact:** Hidden shared state, dead/misleading code.
- **Recommendation:** Remove globals; scope state properly. Playbook RP-12.

### [LOW] Poor naming & inconsistent `this`/`self` (AP-18)
- **File:** `src/AppManager.js:29-33` (single-letter `u,e,p,cid,cc`), `src/AppManager.js:26` (`const self = this`) mixed with `this.db`/`self.db`
- **Description:** Cryptic identifiers and brittle context handling.
- **Recommendation:** Descriptive names; arrow functions / class methods. Playbook RP-03.

## Deprecated APIs
Detected (applicable): legacy **callback-based sqlite3 API** used throughout (modern code uses a
promise wrapper + async/await) and an **in-memory SQLite DB** (`:memory:`) that is non-persistent by
design. To modernize: promisify `db.get/all/run` and use async/await; make the DB path configurable.

## Endpoints preserved / changed in Phase 3
- **Preserved (same URL/method):** `POST /api/checkout` (same body keys), `GET /api/admin/financial-report`, `DELETE /api/users/:id`.
- **Behavior hardened:** admin report + user delete now require an `X-Admin-Token` (was public); delete now cascades to enrollments/payments (was leaving orphans); card/secret no longer logged; payment charging isolated in a service (simulation retained, documented as out-of-scope for a real gateway). `api.http` updated to send the admin token.

================================
Total: 16 findings
================================
