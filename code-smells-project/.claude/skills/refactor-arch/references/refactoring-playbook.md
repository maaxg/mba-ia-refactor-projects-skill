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

## RP-06 · Guard admin/destructive endpoints; remove arbitrary-SQL routes (fixes AP-04, AP-09)

**Before**: `POST /admin/query` runs arbitrary SQL from the body; `DELETE /users/:id` is public.
**After**:
- **Remove** the arbitrary-SQL endpoint entirely (document it in the report). There is no safe MVC
  home for "run any SQL from the internet".
- Put an `auth` middleware on admin/destructive routes; enforce roles (`require_admin`).
- Replace predictable `"fake-jwt-token-"+id` with a real signed token (or clearly mark as out-of-scope
  and gate the route), and never trust client-supplied identity.

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
