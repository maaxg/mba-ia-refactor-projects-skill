# Reference: Anti-Pattern Catalog (Phase 2)

Cross-reference the code against every entry below. Each has **detection signals** (what to grep/read
for) and a **severity**. Severity follows the MVC + SOLID scale:

- **CRITICAL** — architecture/security failures that break correctness, expose sensitive data
  (hardcoded credentials, SQL Injection), or completely destroy separation of concerns (God Class).
- **HIGH** — strong MVC/SOLID violations that badly hurt maintainability/testability (business logic
  trapped in controllers, tight coupling with no DI, global mutable state).
- **MEDIUM** — standardization/duplication/moderate performance issues (N+1 queries, deprecated APIs,
  missing route validation, misused middleware).
- **LOW** — readability: bad naming, magic numbers, `print()` logging, dead code.

This catalog is language-agnostic — the signals are written so they apply to Python, Node.js, Ruby,
PHP, etc. There are **18 anti-patterns** across all four severities (well above the required 8).

---

## CRITICAL

### AP-01 · Hardcoded Credentials / Secrets
**Signals:** literal `SECRET_KEY`, `password`, `api_key`, `token`, DB passwords, payment keys
assigned to string literals in source (`SECRET_KEY = "..."`, `dbPass: "..."`, `pk_live_...`).
**Impact:** secret leakage, unrotatable credentials, repo-history exposure.

### AP-02 · SQL Injection (string-concatenated queries)
**Signals:** SQL built with `+`, f-strings, `.format()`, or template literals injecting request data
(`"... WHERE id='" + id + "'"`, `f"... {email} ..."`). Contrast with parameterized `?` / `%s` / `:name`.
**Impact:** data exfiltration, auth bypass (`' OR '1'='1`), full DB compromise.
**Note:** an ORM's `.like(f"%{q}%")` parameterizes the *value* (not classic SQLi) but leaves `%`/`_`
wildcards unescaped — report as LOW, don't overstate as CRITICAL.

### AP-03 · God Class / God Method / God File
**Signals:** one class/file/function owning DB connection + schema + routing + validation + business
logic; hundreds of lines; many unrelated responsibilities (e.g. `AppManager`, a `models.py` holding
business rules for every domain).
**Impact:** impossible to test in isolation; every change risks everything.

### AP-04 · Unauthenticated / Arbitrary-Execution Admin Endpoint
**Signals:** routes that run arbitrary SQL from the request body, wipe/reset the DB, or expose admin
actions with no auth (`POST /admin/query`, `POST /admin/reset-db`).
**Impact:** remote data destruction / arbitrary DB access. Remove or lock down; document the decision.

### AP-05 · Broken Crypto / Plaintext Passwords
**Signals:** passwords stored/compared in plaintext; MD5/SHA1 without salt; homemade "hashing"
(base64, a pointless iteration loop, truncation); passwords returned in API responses / serializers.
**Impact:** total credential compromise on any DB leak.

---

## HIGH

### AP-06 · Insecure Runtime Config (debug + open bind + open CORS)
**Signals:** `debug=True` / `app.run(debug=True)` in "production"; `host="0.0.0.0"`; `CORS(app)` with
no origin allowlist; secrets returned by a `/health` endpoint.
**Impact:** Werkzeug/dev-debugger RCE if reachable; data exposure; CSRF surface.

### AP-07 · Business Logic in Controllers / Routes (Fat Controller)
**Signals:** route handlers doing pricing, discounts, stock math, notifications, report aggregation
inline; controllers that both handle HTTP and implement domain rules.
**Impact:** untestable, unreusable logic; violates MVC and SRP.

### AP-08 · No Dependency Injection / Tight Coupling / Global Mutable State
**Signals:** module-level mutable globals (`globalCache`, `totalRevenue`, a shared DB connection);
components hard-instantiating their dependencies; a single shared connection reused across threads
(`check_same_thread=False`).
**Impact:** hidden state, race conditions, non-thread-safety, untestable units.

### AP-09 · Missing Authentication / Authorization
**Signals:** create/update/delete/admin/report endpoints with no auth guard; `is_admin()` defined but
never enforced; predictable "tokens" (`"fake-jwt-token-" + id`).
**Impact:** anyone can mutate data or read privileged reports.

### AP-10 · Non-Atomic Multi-Write (no transaction / no rollback)
**Signals:** a flow that inserts an order + items + decrements stock (or enroll + payment + audit)
across several statements with a single late commit and no `try/except → rollback`.
**Impact:** partial failures corrupt data (orphaned rows, wrong stock).

---

## MEDIUM

### AP-11 · N+1 Queries
**Signals:** a query in a loop — fetch list, then per-row fetch a related row
(`for row: cursor.execute(... row.id ...)`; `User.query.get()` inside a per-task loop; `len(u.tasks)`
lazy-load per user). Report aggregation done in app code instead of `SUM()`/`JOIN`.
**Impact:** O(N) round-trips; scales terribly.

### AP-12 · Deprecated APIs  **(required check)**
**Signals (by ecosystem):**
- SQLAlchemy: `Model.query.get(id)` (legacy) → `db.session.get(Model, id)`; `Query` API removed patterns.
- Python stdlib: `datetime.utcnow()` (deprecated 3.12) → `datetime.now(timezone.utc)`.
- Node sqlite3: legacy callback API used where a promise wrapper is expected; `new Buffer()`.
- Express: deprecated body-parser usage, `res.send(status, body)` signature.
- General: anything the framework's changelog marks deprecated/removed for the detected version.
**Impact:** breaks on the next upgrade; warnings; latent bugs.

### AP-13 · Missing / Weak Input Validation
**Signals:** routes reading `request.json` fields with no presence/type/format checks; numeric fields
compared without casting (`preco < 0` on a string → 500); weak email regex (`a@b`); no card/price checks.
**Impact:** 500s, bad data, injection surface.

### AP-14 · Duplicated Code / Duplicated Validation
**Signals:** the same validation/serialization/row→dict mapping copy-pasted across create & update
handlers, or reimplemented inline while a shared helper/`to_dict()` exists but is bypassed.
**Impact:** drift, inconsistent behavior, higher maintenance cost.

### AP-15 · Information Disclosure via Broad Exception Handling
**Signals:** `except Exception as e: return jsonify({"erro": str(e)})` / `catch(e){ res.send(e) }`;
bare `except:` swallowing everything; returning raw DB/error text (incl. SQL) to clients.
**Impact:** leaks internals; hides real bugs; aids attackers.

---

## LOW

### AP-16 · Magic Numbers / Magic Strings
**Signals:** unnamed literals for thresholds, discount rates, ports, status lists, DB paths, versions
scattered in logic (`10000`, `0.1`, `"4"`, `port 3000`, `"loja.db"`).
**Impact:** unclear intent; error-prone edits.

### AP-17 · `print()` / `console.log` as Logging
**Signals:** `print(...)` / `console.log(...)` used for diagnostics and "notifications" instead of a
logging framework; logging secrets/PII (full card numbers) is CRITICAL, not LOW.
**Impact:** no levels, no structure, unstructured ops; possible data leakage.

### AP-18 · Dead Code / Unused Imports / Poor Naming
**Signals:** unused imports and dependencies; a `services/`/`utils/` module never imported; single-
letter identifiers (`u`, `e`, `cc`, `td`); exported values never updated.
**Impact:** confusion, misleading structure, bloat.
