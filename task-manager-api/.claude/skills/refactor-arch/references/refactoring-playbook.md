# Reference: Refactoring Playbook (Phase 3)

Concrete before/after transformations, one per anti-pattern family. Each maps to catalog IDs and to
a target MVC layer. Examples are shown in Python (Flask/sqlite3 & Flask-SQLAlchemy) and Node
(Express/sqlite3) — adapt the same idea to whatever stack you detected. **12 patterns** (≥8 required).

---

## RP-01 · Extract hardcoded config → `config/settings` (fixes AP-01, AP-06, AP-16)

**Before**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
CORS(app)
app.run(host="0.0.0.0", port=5000, debug=True)
```
**After** — `src/config/settings.py`
```python
import os
class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"] if os.environ.get("SECRET_KEY") else os.urandom(24).hex()
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
settings = Settings()
```
Node: `src/config/settings.js` exporting `process.env.*` with defaults; never commit real secrets.

---

## RP-02 · Parameterize SQL / repository in the model (fixes AP-02)

**Before** (SQL injection + auth bypass)
```python
cursor.execute("SELECT * FROM usuarios WHERE email='" + email + "' AND senha='" + senha + "'")
```
**After** — bound params inside `models/usuario_model.py`
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
```
Every query uses `?` / `%s` / `:name` placeholders. No request data ever concatenated into SQL.

---

## RP-03 · Split God class/file → per-domain Models + Controllers (fixes AP-03, AP-07)

**Before**: `models.py` (350 lines) or `AppManager.js` (one class) holds DB + SQL + validation +
business rules + routing for every domain.
**After**: one model per entity (`produto_model.py`, `usuario_model.py`, `pedido_model.py`) owning
only that entity's data access; one controller per domain owning the flow; routing extracted to
`views/routes`. Each file has a single responsibility and is unit-testable in isolation.

---

## RP-04 · Move business logic out of routes → controllers (fixes AP-07)

**Before** (Express route with inline checkout workflow)
```js
app.post("/api/checkout", (req, res) => {
  // create user, fake-charge card, enroll, record payment, audit — all inline, nested callbacks
});
```
**After** — thin route + controller
```js
// src/routes/routes.js
router.post("/api/checkout", (req, res, next) => checkoutController.checkout(req, res, next));
// src/controllers/checkout_controller.js
async function checkout(req, res, next) {
  const user = await userModel.findOrCreate(...);
  const payment = await paymentService.charge(...);      // business rule, not in the route
  const enrollment = await enrollmentModel.create(...);
  res.json({ status: "ok", enrollmentId: enrollment.id });
}
```
Routes only wire URL→controller. Controllers hold the flow. Models hold the data.

---

## RP-05 · Proper password hashing + stop leaking it (fixes AP-05)

**Before**
```python
def set_password(self, pw): self.password = hashlib.md5(pw.encode()).hexdigest()   # unsalted MD5
def to_dict(self): return {"id": self.id, "password": self.password, ...}          # leaked!
```
**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pw): self.senha_hash = generate_password_hash(pw)
def check_password(self, pw): return check_password_hash(self.senha_hash, pw)
def to_dict(self):  # NEVER include the hash
    return {"id": self.id, "nome": self.nome, "email": self.email}
```
Node: use `bcrypt`. Remove the homemade `badCrypto`/base64 "hashing".

---

## RP-06 · Guard EVERY write endpoint; separate authn from authz; remove arbitrary-SQL routes (fixes AP-04, AP-09)

**The rule (do not skip any):** the AP-09 finding lists the endpoints with no auth guard. Guard
**every one of them** — not just the two most obviously "admin/destructive" ones. Concretely:

1. **Enumerate the write endpoints from the Phase 2 audit.** Every route that mutates state —
   `POST` / `PUT` / `PATCH` / `DELETE` on *each* resource the finding named (users, tasks,
   categories, …) — is in scope. If the audit flagged "create/update/delete of users, tasks and
   categories are public", then **all nine** of those (create/update/delete × 3 resources) must end
   up guarded, plus any privileged report route.
2. **Provide two guards, not one:**
   - `require_auth` — a valid signed token of *any* role. Use for ordinary content writes
     (create/update/delete a task, a category, etc.).
   - `require_admin` — a valid token **and** `role == "admin"`. Use for account management
     (create/update/delete users) and privileged reads (global reports, admin overviews).
   Reuse a single `_extract_token()` + `verify_token()` so the two decorators don't drift.
3. **Leave public only what must be public:** `GET` reads (unless the audit said a read is
   privileged), `POST /login`, and health checks. Everything else that writes → a guard.
4. **Remove** any arbitrary-SQL endpoint entirely (document it in the report). There is no safe MVC
   home for "run any SQL from the internet".
5. Replace predictable `"fake-jwt-token-"+id` with a real signed token, and never trust
   client-supplied identity.

**Before**: `POST /admin/query` runs arbitrary SQL; `DELETE /users/:id` is public — **and so are**
`POST/PUT /users`, `POST/PUT/DELETE /tasks`, `POST/PUT/DELETE /categories`.

**After** — one guard module, applied to the *whole* write surface (Flask example):
```python
# src/middlewares/auth.py
def _extract_token():
    h = request.headers.get("Authorization", "")
    return h[7:] if h.startswith("Bearer ") else request.headers.get("X-Auth-Token")

def require_auth(fn):            # any valid token
    @wraps(fn)
    def w(*a, **k):
        if not verify_token(_extract_token()):
            return jsonify({"error": "Autenticação necessária"}), 401
        return fn(*a, **k)
    return w

def require_admin(fn):           # valid token + admin role
    @wraps(fn)
    def w(*a, **k):
        p = verify_token(_extract_token())
        if not p:      return jsonify({"error": "Autenticação necessária"}), 401
        if p.get("role") != "admin":
            return jsonify({"error": "Acesso restrito a administradores"}), 403
        return fn(*a, **k)
    return w
```
```python
# src/views/task_routes.py — EVERY write wired through a guard
bp.add_url_rule("/tasks", "create_task", require_auth(c.create_task), methods=["POST"])
bp.add_url_rule("/tasks/<int:id>", "update_task", require_auth(c.update_task), methods=["PUT"])
bp.add_url_rule("/tasks/<int:id>", "delete_task", require_auth(c.delete_task), methods=["DELETE"])
# users → require_admin (account management); reports/summary → require_admin; GET reads stay public
```
Node/Express: an `authMiddleware` / `adminMiddleware` pair applied to every mutating route in the
router. **Self-check before finishing:** re-read the AP-09 finding and confirm each write endpoint it
named now has a decorator — if any `POST/PUT/PATCH/DELETE` from the finding is still bare, the fix is
incomplete.

---

## RP-07 · Wrap multi-write flows in a transaction (fixes AP-10)

**Before**: insert order → insert items → decrement stock, one late `commit()`, no rollback.
**After**
```python
try:
    conn.execute("BEGIN")
    pedido_id = pedido_model.insert(conn, ...)
    for item in itens:
        pedido_model.insert_item(conn, pedido_id, item)
        produto_model.decrement_stock(conn, item.produto_id, item.qtd)
    conn.commit()
except Exception:
    conn.rollback()
    raise
```
SQLAlchemy: use `db.session.begin()` / commit-or-rollback. All-or-nothing.

---

## RP-08 · Fix N+1 with JOIN / eager load / aggregate (fixes AP-11)

**Before**
```python
for pedido in pedidos:
    for item in itens_do_pedido(pedido.id):
        nome = cursor.execute("SELECT nome FROM produtos WHERE id=?", (item.produto_id,))  # per row
```
**After** — one JOIN
```sql
SELECT ip.*, p.nome FROM itens_pedido ip JOIN produtos p ON p.id = ip.produto_id WHERE ip.pedido_id IN (...)
```
SQLAlchemy: `db.session.query(Task).options(joinedload(Task.category), joinedload(Task.user))`.
Reports: compute with `SUM()`/`GROUP BY` in SQL, not by looping in app code.

---

## RP-09 · Replace deprecated APIs (fixes AP-12)

| Deprecated | Replacement |
|---|---|
| `Model.query.get(id)` (SQLAlchemy legacy) | `db.session.get(Model, id)` |
| `datetime.utcnow()` (Py 3.12+) | `datetime.now(timezone.utc)` |
| sqlite3 callback pyramid (Node) | promisify / `async-await` wrapper around `db.get/all/run` |
| `new Buffer(x)` | `Buffer.from(x)` |

Apply the current equivalent for the detected runtime version.

---

## RP-10 · Centralize error handling in middleware (fixes AP-15)

**Before**: every handler `except Exception as e: return jsonify({"erro": str(e)})` (leaks internals).
**After** — Flask
```python
# src/middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle(e):
        app.logger.exception(e)                      # full detail server-side
        code = getattr(e, "code", 500)
        return jsonify({"error": "Internal error" if code == 500 else str(e)}), code
```
Express: an `(err, req, res, next)` error middleware registered last. Controllers `throw`/`next(err)`
instead of formatting errors themselves. Clients never see raw DB/SQL text.

---

## RP-11 · Add input validation at the boundary (fixes AP-13, AP-14)

**Before**: `if data["preco"] < 0` on an unchecked string field, duplicated across create & update.
**After**: one shared validator (a schema — marshmallow/pydantic/Joi/zod — or a small helper) invoked
by the controller. Validate presence, type, range, and format (proper email regex) **once**; reuse it
for both create and update. Return 400 with a clear message on failure.

---

## RP-12 · Named constants + real logging (fixes AP-16, AP-17, AP-18)

**Before**
```python
if total > 10000: desconto = total * 0.1     # magic numbers
print("pedido criado")                        # print as logging
```
**After**
```python
# src/config/constants.py
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
# in code
import logging; logger = logging.getLogger(__name__)
logger.info("pedido criado id=%s", pedido_id)
```
Remove dead code and unused imports; give variables meaningful names; move constants to one place.
**Never** log secrets or full card numbers (that's a CRITICAL leak, not a LOW smell).
