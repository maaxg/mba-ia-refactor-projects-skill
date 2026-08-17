```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors 4.0.0; marshmallow / requests / python-dotenv (declared but UNUSED)
Domain:        Task Manager API (tasks, users, categories)
Architecture:  Partially organized — models/ routes/ services/ utils/ exist, but services/ and
               utils/ are dead code; business logic still lives in the route handlers
Source files:  15 Python files analyzed (~1160 lines)
DB tables:     tasks, users, categories (SQLite via SQLAlchemy ORM)
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy)
Files:   15 analyzed | ~1160 lines of code
Date:    2026-08-11

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 4 | LOW: 3
Total: 17 findings

## Findings

### [CRITICAL] Hardcoded Flask SECRET_KEY (AP-01)
- **File:** `app.py:13`
- **Description:** `SECRET_KEY = 'super-secret-key-123'` hardcoded in source.
- **Impact:** Session/token forgery; unrotatable; exposed in git history.
- **Recommendation:** Load from env in `config/settings.py`. Playbook RP-01.

### [CRITICAL] Hardcoded SMTP credentials (AP-01)
- **File:** `services/notification_service.py:9-10`
- **Description:** `email_user='taskmanager@gmail.com'` and `email_password='senha123'` embedded in the service.
- **Impact:** Mailbox credential leak.
- **Recommendation:** Env-based config; no secrets in code. Playbook RP-01.

### [CRITICAL] Passwords hashed with unsalted MD5 (AP-05)
- **File:** `models/user.py:29` (`set_password`), `models/user.py:32` (`check_password`)
- **Description:** `hashlib.md5(pwd).hexdigest()` — fast, unsalted, broken for passwords.
- **Impact:** Trivial offline cracking / rainbow tables on any DB leak.
- **Recommendation:** `werkzeug.security.generate_password_hash` / `check_password_hash`. Playbook RP-05.

### [CRITICAL] Password hash exposed in API responses (AP-05)
- **File:** `models/user.py:16-25` (`to_dict` includes `'password'`); returned at `routes/user_routes.py:209` (login), `:85-86` (create), `:33` (get), `:129` (update)
- **Description:** The serializer leaks the stored password hash on every user payload.
- **Impact:** Hash disclosure to any API client.
- **Recommendation:** Remove `password` from `to_dict`. Playbook RP-05.

### [CRITICAL] Interactive debugger enabled + bind all interfaces (AP-06)
- **File:** `app.py:34`
- **Description:** `app.run(debug=True, host='0.0.0.0', port=5000)`.
- **Impact:** Werkzeug debugger = RCE if reachable; exposed on all interfaces.
- **Recommendation:** Config-driven `debug`/`host`, off by default. Playbook RP-01.

### [HIGH] No authentication/authorization on any endpoint (AP-09)
- **File:** every route, e.g. `routes/user_routes.py:42` (create), `:134` (delete); `is_admin()` defined at `models/user.py:34` but never enforced
- **Description:** Create/update/delete of users, tasks and categories are fully public.
- **Impact:** Anyone can mutate or destroy data.
- **Recommendation:** `require_auth`/`require_admin` middleware; enforce roles. Playbook RP-06.
- **Resolution (Phase 3):** `require_auth` guard on **all 6** task/category writes (`POST/PUT/DELETE`
  `/tasks`, `POST/PUT/DELETE /categories`); `require_admin` on **all 3** user writes
  (`POST/PUT/DELETE /users`) and on `GET /reports/summary`. Every write endpoint named by this
  finding is now guarded — `GET` reads and `POST /login` stay public. Verified live (401 without a
  token, 403 for non-admin on admin routes, 200/201 with a valid token).

### [HIGH] Fake / predictable auth token (AP-09)
- **File:** `routes/user_routes.py:210`
- **Description:** Login returns `'fake-jwt-token-' + str(user.id)` — guessable, unsigned, no expiry.
- **Impact:** Token forgery; no real session security.
- **Recommendation:** Signed token (itsdangerous with SECRET_KEY) or real JWT. Playbook RP-06.

### [HIGH] N+1 queries in GET /tasks (AP-11)
- **File:** `routes/task_routes.py:41-57`
- **Description:** For each task, `User.query.get()` and `Category.query.get()` run inside the loop.
- **Impact:** O(N) extra round-trips per listing.
- **Recommendation:** Eager-load (`joinedload`) user/category. Playbook RP-08.

### [HIGH] N+1 queries in reports, users and categories (AP-11)
- **File:** `routes/report_routes.py:53-68` (per-user task query), `routes/report_routes.py:157-165` (per-category count), `routes/user_routes.py:22` (`len(u.tasks)` lazy-load per user)
- **Description:** Aggregations done by looping queries instead of `GROUP BY`/aggregate SQL.
- **Impact:** Report cost scales with users×categories.
- **Recommendation:** Aggregate queries. Playbook RP-08.

### [HIGH] Dead service/utils layer; model helpers bypassed (AP-18/AP-07)
- **File:** `services/notification_service.py` (never imported); `utils/helpers.py:57-108` (`process_task_data` never imported; `format_date`/`calculate_percentage` imported at `report_routes.py:7` but unused); `Task.is_overdue()` (`models/task.py:50-60`) re-implemented inline at `task_routes.py:30-39, 71-80`, `user_routes.py:171-180`, `report_routes.py:33-43`; `Task.validate_status`/`validate_priority` (`models/task.py:38-48`) never used
- **Description:** The "layers" are folders only — the real logic lives duplicated in the routes.
- **Impact:** Duplication, drift, untestable; the structure misleads.
- **Recommendation:** Real controllers/services; reuse model methods. Playbook RP-03, RP-04.

### [MEDIUM] Deprecated APIs: Query.get() + datetime.utcnow() (AP-12)
- **File:** `Query.get()` at `task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227`, `user_routes.py:29, 94, 136, 155`, `report_routes.py:105, 192, 213`; `datetime.utcnow()` at `models/task.py:15, 16, 52`, `models/user.py:14`, `models/category.py:11`, `task_routes.py:31, 72, 285`, `user_routes.py:172`, `report_routes.py:35, 42, 45, 71, 133`, `seed.py:66, 69`
- **Description:** `Model.query.get(id)` is the legacy SQLAlchemy 1.x pattern (2.0 → `db.session.get`); `datetime.utcnow()` is deprecated in Python 3.12+ (emits a warning on this 3.13 runtime).
- **Impact:** Breaks on upgrade; deprecation warnings; tz-naive bugs.
- **Recommendation:** `db.session.get(Model, id)`; `datetime.now(timezone.utc)`. Playbook RP-09.

### [MEDIUM] Bare `except:` swallowing all errors (AP-15)
- **File:** `task_routes.py:62` (wraps the whole get_tasks body → generic 500), `task_routes.py:236`; `user_routes.py:130, 149`; `report_routes.py:186, 207, 221`
- **Description:** Broad/bare excepts hide the real error and return a generic message.
- **Impact:** Masks bugs; inconsistent error contract.
- **Recommendation:** Centralized error handler; catch specific exceptions. Playbook RP-10.

### [MEDIUM] No config/DI layer; hardcoded DB URI; unused deps (AP-08/AP-16)
- **File:** `app.py:11` (`sqlite:///tasks.db` hardcoded); `requirements.txt:4-6` (marshmallow/requests/python-dotenv declared but never used)
- **Description:** No configuration management or dependency injection; routes reach `db.session` directly (`task_routes.py:146-154`).
- **Impact:** Tight coupling; env-specific config impossible; dependency bloat.
- **Recommendation:** `config/settings.py` from env; thin routes → controllers. Playbook RP-01, RP-04.

### [MEDIUM] Unvalidated numeric inputs → 500 (AP-13)
- **File:** `task_routes.py:113, 182` (compare `priority < 1` with no `int()` cast — string priority raises TypeError); `task_routes.py:261, 264` (`int(priority)`/`int(user_id)` on query params, no guard)
- **Description:** Malformed numeric input crashes with an unhandled 500.
- **Impact:** Fragile endpoints.
- **Recommendation:** Shared validators / marshmallow schemas at the boundary. Playbook RP-11.

### [LOW] Magic literals; constants defined but ignored (AP-16)
- **File:** `utils/helpers.py:110-116` defines `VALID_STATUSES`, `VALID_ROLES`, `MAX/MIN_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH`, etc., but routes hardcode the literals: status list `task_routes.py:110, 177`; title 3/200 `:96, 99, 167, 169`; priority 1/5 `:113, 182`; password len `user_routes.py:64, 115`; roles `:71, 120`
- **Recommendation:** Import and use the constants. Playbook RP-12.

### [LOW] print() used as logging (AP-17)
- **File:** `task_routes.py:149, 153, 219, 234`; `user_routes.py:83, 89, 147`; `services/notification_service.py:21, 24`; `utils/helpers.py:39, 41`
- **Recommendation:** Use the `logging` module. Playbook RP-12.

### [LOW] Pervasive unused imports + import-time db.create_all() (AP-18)
- **File:** unused imports `app.py:7`, `task_routes.py:7`, `user_routes.py:6`, `report_routes.py:8`, `models/task.py:3`, `helpers.py:3-7`; `db.create_all()` side effect at `app.py:30-31`
- **Recommendation:** Remove dead imports; run schema creation inside the app factory. Playbook RP-12.

## Deprecated APIs
Detected (applicable): **SQLAlchemy `Model.query.get(id)`** (legacy 1.x; 2.0 → `db.session.get(Model, id)`)
across all route files, and **`datetime.utcnow()`** (deprecated in Python 3.12+, warns on this 3.13
runtime) across models, routes and seed. Replace with `db.session.get(...)` and a tz-aware/naive-UTC
helper respectively.

## Endpoints preserved / changed in Phase 3
- **Preserved (same URL/method/response):** `/health`, `/`, `/tasks` (GET/POST), `/tasks/<id>` (GET/PUT/DELETE), `/tasks/search`, `/tasks/stats`, `/users` (GET/POST), `/users/<id>` (GET/PUT/DELETE), `/users/<id>/tasks`, `/login`, `/reports/user/<id>`, `/reports/summary`, `/categories` (GET/POST), `/categories/<id>` (PUT/DELETE). The `password` field is removed from user payloads (security fix).
- **Auth guard (RP-06) — applied to every write endpoint AP-09 flagged, not a subset:**

  | Endpoint | Guard | Unauth | Non-admin |
  |---|---|---|---|
  | `POST /tasks`, `PUT /tasks/<id>`, `DELETE /tasks/<id>` | `require_auth` | 401 | ok |
  | `POST /categories`, `PUT /categories/<id>`, `DELETE /categories/<id>` | `require_auth` | 401 | ok |
  | `POST /users`, `PUT /users/<id>`, `DELETE /users/<id>` | `require_admin` | 401 | 403 |
  | `GET /reports/summary` | `require_admin` | 401 | 403 |
  | `GET` reads, `POST /login`, `/health`, `/` | public | — | — |

  Rationale: ordinary content writes (tasks, categories) require any authenticated user; account
  management and the global report require an admin (`is_admin()`, previously defined but never
  enforced, is now enforced).
- **Behavior hardened:** `POST /login` now returns a real signed token (itsdangerous). Two guards
  (`require_auth`, `require_admin`) share one `_extract_token()`+`verify_token()` in
  `middlewares/auth.py`. Validation logs in as admin (`joao@email.com`) and as a plain user
  (`maria@email.com`) and exercises the full matrix above.

================================
Total: 17 findings
================================
