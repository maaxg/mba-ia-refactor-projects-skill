# Reference: Target MVC Architecture Guidelines (Phase 3)

The refactor target is a clean **Model-View-Controller** layout under `src/`. Keep it identical in
spirit across languages — only the file extensions and framework glue change.

## Target directory structure

```
src/
├── config/
│   └── settings.(py|js)        # ALL config from env vars (with safe defaults). NO secrets in code.
├── models/
│   ├── <entity>_model.(py|js)  # one module per domain entity; owns data access for that entity
│   └── ...
├── views/  (a.k.a. routes/)
│   └── routes.(py|js)          # ONLY maps URL+method → controller function. No logic. No DB.
├── controllers/
│   ├── <domain>_controller.(py|js)  # orchestrates request → model calls → response. Business flow.
│   └── ...
├── middlewares/
│   ├── error_handler.(py|js)   # centralized error handling (one place, safe messages)
│   └── auth.(py|js)            # auth/authorization guard (when the domain needs it)
└── app.(py|js)                 # composition root / entry point: wires config, models, controllers, routes
```

## Layer responsibilities (the contract)

### Models (data + domain state)
- The **only** layer that talks to the database. Owns queries / ORM access for its entity.
- All SQL is **parameterized** (bound params, never string concatenation).
- Encapsulates entity-level rules and serialization (`to_dict()` that **never** exposes password/secret fields).
- No HTTP awareness (no `request`/`response`).

### Views / Routes (HTTP surface)
- Declares the routes and binds each to a controller function.
- **Thin**: no business logic, no DB access, no validation logic beyond wiring. Preserves the
  original URLs, methods, and response shapes exactly.

### Controllers (orchestration / business flow)
- Receives the parsed request, validates input (or calls a validator), calls one or more models,
  applies business rules that span entities, shapes the response.
- Does **not** build SQL and does **not** define routes. Depends on models via injection/import,
  not on globals.

### Middlewares
- **error_handler**: one centralized handler that turns exceptions into safe, consistent responses
  (no `str(e)` leakage to clients; log the detail server-side).
- **auth**: guards protected/admin/destructive endpoints; enforces roles where `is_admin()`-style
  checks exist.

### Config
- A single module reading from environment variables with sensible non-secret defaults.
- `SECRET_KEY`, DB URIs, payment keys, SMTP creds → env only. `debug` off by default; bind host
  configurable (not hardcoded `0.0.0.0` in prod). CORS origins configurable (no blanket allow).

### Entry point (composition root)
- `app.py` / `app.js`: creates the app, loads config, initializes the DB/connection, registers
  middlewares, mounts the routes, and starts the server. This is the ONLY place that wires things
  together — the "composition root". No business logic here.

## Cross-cutting requirements

- **HTTP contract preserved**: same endpoints in, same responses out (except documented dangerous
  endpoints that are removed/locked down).
- **Config extracted**: zero hardcoded secrets remain.
- **Models abstract data**; **Views route**; **Controllers hold the flow**; **errors centralized**;
  **entry point clear**.
- **Dependency direction**: routes → controllers → models → db. Never the reverse; no layer reaches
  around another (routes must not touch the DB; models must not import controllers).
- **Deprecated APIs replaced** with their current equivalents.
