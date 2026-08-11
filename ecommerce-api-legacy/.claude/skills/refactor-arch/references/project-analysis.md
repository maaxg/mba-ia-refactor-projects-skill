# Reference: Project Analysis Heuristics (Phase 1)

Goal: detect **language**, **framework + version**, **database**, **domain/entities**, and the
**current architecture** — without modifying anything. Everything here is language-agnostic; use the
signals that match what you find.

## 1. Language detection (by files present)

| Signal file(s) | Language |
|---|---|
| `requirements.txt`, `pyproject.toml`, `*.py`, `Pipfile` | Python |
| `package.json`, `*.js`, `*.ts`, `*.mjs` | Node.js / JavaScript / TypeScript |
| `Gemfile`, `*.rb` | Ruby |
| `composer.json`, `*.php` | PHP |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |

Confirm by counting source files per extension. The dominant extension is the primary language.

## 2. Framework + version detection (read the manifest)

Open the dependency manifest and read the declared framework and version. Do **not** guess a version —
read it. If a lockfile exists (`package-lock.json`, `poetry.lock`), it holds the resolved version.

| Language | Where to look | Framework markers |
|---|---|---|
| Python | `requirements.txt` / `pyproject.toml` | `flask`, `django`, `fastapi`, `starlette`; `flask-sqlalchemy`, `flask-cors` |
| Node.js | `package.json` `dependencies` + lockfile | `express`, `@nestjs/core`, `fastify`, `koa` |
| Ruby | `Gemfile` | `rails`, `sinatra` |
| PHP | `composer.json` | `laravel/framework`, `symfony/*` |

Also note the **entry point**: `main`/`scripts.start` in `package.json`; the file that calls
`app.run()` / `app.listen()` / `create_app()`; the `if __name__ == "__main__"` block in Python.

## 3. Database detection

- **ORM present?** `flask_sqlalchemy` / `SQLAlchemy`, `django.db.models`, `sequelize`, `prisma`,
  `typeorm`, `mongoose`, `ActiveRecord`. If yes → models are ORM classes.
- **Raw driver?** `sqlite3`, `psycopg2`, `mysql2`, `pg`, `pymongo`. If yes → look for hand-written
  SQL strings (and, critically, whether they are parameterized or concatenated — that decides SQLi).
- **Which engine?** SQLite (`*.db`, `:memory:`, `sqlite3`), Postgres, MySQL, MongoDB.
- **Schema source?** DDL in code (`CREATE TABLE ...`), migrations folder, or ORM model definitions.
- Record the **tables / collections** and their columns — read the DDL or model classes.

## 4. Domain inference

Infer what the app *does* from: route paths, table names, model names, and seed data. Summarize in
one line, e.g. "E-commerce API (produtos, pedidos, usuários)" or "LMS checkout (users, courses,
enrollments, payments)". List the main entities.

## 5. Current architecture mapping

Classify the current state (this drives how aggressive the refactor must be):

- **Monolithic / single-file**: everything (routing + business logic + DB) in one or a few files.
- **God class**: one class/module owns DB connection, schema, routing, and business logic
  (e.g. `AppManager`, `models.py` doing everything). CRITICAL structural smell.
- **Flat, unlayered**: multiple files but no models/controllers/views separation
  (e.g. `app.py` + `controllers.py` + `models.py` where "models" also holds business logic).
- **Partially layered**: has `models/`, `routes/`, `services/`, `utils/` folders — but check whether
  the layers are *real* or **dead code** (services/utils that are never imported while the business
  logic still lives in the routes). Partial organization still has plenty of findings.

Note where each responsibility currently lives (routing / validation / business logic / data access /
config) — you'll move them in Phase 3.

## 6. Source-file counting

Count only real source files. **Exclude**: lockfiles, `node_modules/`, `__pycache__/`, `.venv/`,
generated files, and `.claude/`. Report the honest count (it must match reality — the checklist
verifies this).

## Output

Emit the `PHASE 1: PROJECT ANALYSIS` block defined in `SKILL.md`, filled from the above.
