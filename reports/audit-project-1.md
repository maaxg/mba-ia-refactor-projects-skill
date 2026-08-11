```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, usuários, pedidos, itens_pedido)
Architecture:  Flat / unlayered — app.py + controllers.py + models.py + database.py,
               with business logic and raw SQL mixed into "models" and controllers
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido (SQLite via stdlib sqlite3)
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Date:    2026-08-11

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 3
Total: 16 findings

## Findings

### [CRITICAL] SQL Injection across the entire data layer (AP-02)
- **File:** `models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-160, 163-166, 174, 188, 192, 220, 224, 279-281, 289-297`; also `app.py:59-78`
- **Description:** Every query is built by string concatenation with request data (e.g. `"SELECT * FROM produtos WHERE id = " + str(id)`), including the search builder (`models.py:289-297`). `database.py:70-82` proves parameterization was known (`?` used for seeds) yet abandoned everywhere else.
- **Impact:** Data exfiltration, tampering, and full DB compromise via crafted input.
- **Recommendation:** Move all data access into per-entity models using bound parameters (`?`). Playbook RP-02.

### [CRITICAL] Authentication bypass via SQLi in login (AP-02/AP-05)
- **File:** `models.py:109-111`
- **Description:** `SELECT * FROM usuarios WHERE email = '<email>' AND senha = '<senha>'` concatenates raw input — a classic `' OR '1'='1` bypass. Passwords are also compared in plaintext.
- **Impact:** Any account (including admin) can be logged into without credentials.
- **Recommendation:** Parameterized query + hashed password comparison (`check_password_hash`). Playbook RP-02, RP-05.

### [CRITICAL] Arbitrary SQL execution & unauthenticated DB reset (AP-04)
- **File:** `app.py:59-78` (`POST /admin/query`), `app.py:47-57` (`POST /admin/reset-db`)
- **Description:** `/admin/query` runs any SQL sent in the request body; `/admin/reset-db` wipes all four tables. Both are public — no auth.
- **Impact:** Remote arbitrary DB access and total data destruction by anyone.
- **Recommendation:** Remove `/admin/query` entirely (no safe MVC home for it); gate `/admin/reset-db` behind auth. Playbook RP-06.

### [CRITICAL] Hardcoded secret key, leaked over HTTP (AP-01)
- **File:** `app.py:7`; leaked at `controllers.py:289`
- **Description:** `SECRET_KEY = "minha-chave-super-secreta-123"` is hardcoded and then returned verbatim by `GET /health` (alongside `debug`, `db_path`, `ambiente=producao`).
- **Impact:** Anyone hitting `/health` reads the app secret; secret is unrotatable and in git history.
- **Recommendation:** Load from env in `config/settings.py`; never return secrets from any endpoint. Playbook RP-01.

### [CRITICAL] Plaintext passwords stored and returned (AP-05)
- **File:** seeds `database.py:76-78`; returned at `models.py:83, 99`; created unhashed at `models.py:126-129`
- **Description:** Passwords are seeded and stored in clear text (`admin123`, `123456`), returned by `GET /usuarios` and `GET /usuarios/<id>`, and never hashed on create.
- **Impact:** Total credential compromise on any read/leak.
- **Recommendation:** Hash with `werkzeug.security`; drop `senha` from serialization. Playbook RP-05.

### [HIGH] God file: models.py mixes data access + business logic for 4 domains (AP-03/AP-07)
- **File:** `models.py:1-315`
- **Description:** One module owns raw SQL, order pricing/stock logic (`criar_pedido` 133-169), and sales-report discount math (`relatorio_vendas` 235-273) for produtos, usuarios, pedidos and itens.
- **Impact:** Impossible to test in isolation; any change risks every domain.
- **Recommendation:** Split into per-domain models + controllers. Playbook RP-03, RP-04.

### [HIGH] Insecure runtime config: debug + 0.0.0.0 + open CORS (AP-06)
- **File:** `app.py:8` (`DEBUG=True`), `app.py:88` (`app.run(host="0.0.0.0", debug=True)`), `app.py:9` (`CORS(app)`); self-declared `"ambiente": "producao"` at `controllers.py:286`
- **Description:** Werkzeug interactive debugger enabled in a "production" app, bound to all interfaces, with wide-open CORS.
- **Impact:** Remote code execution via the debugger if reachable; CSRF/data-exposure surface.
- **Recommendation:** Config-driven `debug`/`host`/CORS origins, off by default. Playbook RP-01.

### [HIGH] Global mutable shared DB connection, not thread-safe (AP-08)
- **File:** `database.py:4` (global `db_connection`), `database.py:10` (`check_same_thread=False`)
- **Description:** A single module-level connection is shared across all requests/threads; `get_db()` also performs DDL + seeding as an import-time side effect.
- **Impact:** Race conditions, cursor corruption under concurrency, untestable global state.
- **Recommendation:** Per-request connection / injected data layer; separate schema init from access. Playbook RP-08 target layering.

### [HIGH] Non-atomic order creation with no rollback (AP-10)
- **File:** `models.py:133-169`
- **Description:** `criar_pedido` validates stock, inserts the order + items, and decrements stock across many statements with a single late `commit()` (168) and no `try/except → rollback`.
- **Impact:** A mid-flow failure corrupts stock and leaves orphaned rows.
- **Recommendation:** Wrap the whole flow in a transaction with rollback. Playbook RP-07.

### [HIGH] Business logic in the wrong layers (AP-07)
- **File:** notifications in the controller `controllers.py:208-210, 247-250`; discount/ticket math in the model `models.py:256-272`
- **Description:** Email/SMS/push "notifications" are `print`ed from the controller; sales-report business rules live in the data layer.
- **Impact:** Logic is unreusable and untestable; violates MVC/SRP.
- **Recommendation:** Notifications → a service; report rules → a controller/service; models only fetch data. Playbook RP-04.

### [MEDIUM] N+1 queries in order listing (AP-11)
- **File:** `models.py:171-201` (`get_pedidos_usuario`), `models.py:203-233` (`get_todos_pedidos`)
- **Description:** Loops orders → items → one extra product-name query per item (`cursor2`/`cursor3` per row).
- **Impact:** O(N·M) round-trips; degrades badly with data volume.
- **Recommendation:** Single JOIN across pedidos/itens_pedido/produtos. Playbook RP-08.

### [MEDIUM] Information disclosure via broad exception handling (AP-15)
- **File:** `controllers.py:12, 22, 62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292`
- **Description:** Every handler does `except Exception as e: return jsonify({"erro": str(e)})`, echoing internal/DB/SQL error text to clients.
- **Impact:** Leaks internals; aids attackers; inconsistent error contract.
- **Recommendation:** Centralized error-handler middleware with safe messages + server-side logging. Playbook RP-10.

### [MEDIUM] Missing / weak input validation (AP-13)
- **File:** `controllers.py:43-46, 87-90` (numeric compares without casting), `controllers.py:119-121` (unguarded `float()`); no email-format check at `controllers.py:157, 170-171`
- **Description:** Numeric fields compared (`preco < 0`) without type-casting → `TypeError`/500 on non-numeric JSON; query-param `float()` unguarded; emails unvalidated.
- **Impact:** 500s on malformed input, bad data.
- **Recommendation:** Shared validator (schema) at the boundary. Playbook RP-11.

### [MEDIUM] Duplicated validation logic (AP-14)
- **File:** `controllers.py:24-62` (`criar_produto`) vs `controllers.py:64-96` (`atualizar_produto`)
- **Description:** Presence/range/category validation is copy-pasted across create and update.
- **Impact:** Drift and inconsistent rules over time.
- **Recommendation:** Extract one reusable product validator. Playbook RP-11.

### [LOW] Magic numbers / magic strings (AP-16)
- **File:** discount thresholds/rates `models.py:257-262`; `categorias_validas` `controllers.py:52`; status list `controllers.py:242`; `db_path="loja.db"` `database.py:5`; version string `app.py:36`, `controllers.py:285`
- **Description:** Unnamed literals scattered through logic.
- **Recommendation:** Move to named constants / config. Playbook RP-12.

### [LOW] `print()` used as logging (AP-17)
- **File:** `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250`; `app.py:56, 83-86`
- **Description:** Diagnostics and "notifications" via `print` instead of a logging framework.
- **Recommendation:** Use `logging`. Playbook RP-12.

### [LOW] Duplicated row→dict mapping (AP-18)
- **File:** `models.py:12-21, 31-40, 79-86, 95-102, 304-313`
- **Description:** The same manual row→dict serialization is repeated in nearly every model function.
- **Recommendation:** Single serializer per entity in its model. Playbook RP-03.

## Deprecated APIs
None detected for the target runtime (Flask 3.1.1 / Python 3.13; stdlib `sqlite3` used with its current API). Deprecated-API detection is exercised in Projects 2 and 3.

## Endpoints preserved / changed in Phase 3
- **Preserved (same URL/method/response):** `GET /`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /produtos`, `PUT /produtos/<id>`, `DELETE /produtos/<id>`, `GET /usuarios`, `GET /usuarios/<id>`, `POST /usuarios`, `POST /login`, `POST /pedidos`, `GET /pedidos`, `GET /pedidos/usuario/<id>`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `GET /health` (secret removed from payload).
- **Removed or locked down (justification):** `POST /admin/query` — **removed** (arbitrary SQL execution, no safe MVC home). `POST /admin/reset-db` — kept but **gated behind an admin guard** (destructive).

================================
Total: 16 findings
================================
