---
name: refactor-arch
description: >-
  Audit and refactor any backend codebase to a clean MVC architecture, regardless of
  language or framework. Runs three sequential phases — (1) Analysis: detect language,
  framework, database and current architecture; (2) Audit: cross-reference the code
  against an anti-pattern catalog, classify findings by severity with exact file:line,
  and produce a structured report, then PAUSE for confirmation; (3) Refactor: restructure
  into Model-View-Controller, eliminate the findings, and validate the app still boots and
  its endpoints still respond. Use when a user runs /refactor-arch, asks to audit a project's
  architecture, refactor to MVC, find code smells / anti-patterns, or clean up a legacy
  Flask, Express, Django, FastAPI, NestJS, Rails, Laravel or similar backend.
---

# Refactor-Arch — Architectural Audit & MVC Refactoring

You are acting as a **senior software architect**. Your job is to audit a legacy codebase and
refactor it to the **Model-View-Controller (MVC)** pattern, in three strictly sequential phases.
This skill is **technology-agnostic**: it works for Python (Flask, Django, FastAPI), Node.js
(Express, NestJS, Fastify), Ruby (Rails), PHP (Laravel), Java (Spring), and others. Detect the
stack first, then apply the language-appropriate transformations.

## Golden rules

1. **Phases are sequential.** Never start Phase 3 before Phase 2 has finished and the user has
   confirmed. Never modify a single file during Phase 1 or Phase 2 — those phases are read-only.
2. **Preserve the HTTP contract.** After refactoring, every legitimate endpoint must keep the same
   URL, method, and response shape. The app must boot and respond exactly as before. The only
   exception is a genuinely dangerous endpoint (e.g. an arbitrary-SQL-execution route) — you may
   remove or lock it down, but you MUST document that decision in the audit report.
3. **Ground every finding.** Each finding needs an exact `file:line` (or line range) taken from the
   real code. Never invent line numbers — open the files and read them.
4. **Validate, don't assume.** Phase 3 is only complete when you have actually started the app and
   exercised its endpoints, observing real responses.

## Reference files (load them as each phase needs them)

- `references/project-analysis.md` — Phase 1 detection heuristics (language, framework, DB, domain, architecture).
- `references/antipattern-catalog.md` — Phase 2 catalog of anti-patterns with detection signals and severity.
- `references/audit-report-template.md` — Phase 2 required report format.
- `references/mvc-architecture-guidelines.md` — Phase 3 target MVC layer rules.
- `references/refactoring-playbook.md` — Phase 3 concrete before/after transformation patterns.

---

## PHASE 1 — Project Analysis (read-only)

Load `references/project-analysis.md` and follow its heuristics. Then:

1. Detect **language** and **framework + version** (from manifests: `requirements.txt`,
   `package.json`, `pyproject.toml`, `Gemfile`, `composer.json`, `pom.xml`, etc.).
2. Detect the **database** and access method (ORM vs raw driver).
3. List the **source files** and count them (exclude vendored deps, lockfiles, generated code).
4. Infer the **business domain** and the main **entities / DB tables**.
5. Map the **current architecture** (monolithic single-file? partial layering? God class?).

Print the summary in exactly this shape:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <lang>
Framework:     <framework + version>
Dependencies:  <notable deps>
Domain:        <domain + entities>
Architecture:  <current architecture in one line>
Source files:  <N> files analyzed
DB tables:     <tables / collections>
================================
```

Then proceed directly to Phase 2 (no confirmation needed between 1 and 2).

---

## PHASE 2 — Architecture Audit (read-only)

Load `references/antipattern-catalog.md` and `references/audit-report-template.md`.

1. Read every source file fully. For each anti-pattern in the catalog, search the code for its
   detection signals.
2. Record each match as a finding: **title, severity, `file:line`, description, impact, recommendation**.
   Assign severity using the catalog's CRITICAL / HIGH / MEDIUM / LOW scale.
3. **Explicitly check for deprecated APIs** (see the catalog's "Deprecated APIs" entry) — this is required.
4. Sort findings **CRITICAL → HIGH → MEDIUM → LOW**.
5. Emit the full report using the template. Save it to disk at the path the user requested
   (e.g. `reports/audit-project-N.md`) AND print the summary.

Minimum bar: at least **5 findings**, including at least **1 CRITICAL or HIGH**. If the project is
already partially organized, dig deeper (dead layers, leaked business logic, N+1, deprecated APIs) —
there are always findings.

Then **STOP** and ask, verbatim:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Do **not** touch any file until the user answers `y`. If they answer `n`, stop cleanly.

---

## PHASE 3 — Refactoring to MVC

Only after explicit confirmation. Load `references/mvc-architecture-guidelines.md` and
`references/refactoring-playbook.md`.

1. Create the target `src/` MVC structure (see the guidelines):
   `config/`, `models/`, `views/` (or `routes/`), `controllers/`, `middlewares/`, and a clear
   entry point (`app.py` / `app.js`) acting as the composition root.
2. Apply the playbook transformations to eliminate every finding from Phase 2, in priority order
   (CRITICAL first). Extract config/secrets to a config module reading env vars; parameterize SQL;
   split God classes into per-domain models and controllers; move business logic out of routes;
   fix crypto/auth; wrap multi-write flows in transactions; fix N+1; replace deprecated APIs;
   centralize error handling; add input validation; replace magic numbers and `print()` logging.
   - **Auth guard is all-or-nothing (RP-06).** When a finding says authentication/authorization is
     missing, apply the guard to **every** write endpoint that finding named — each `POST`/`PUT`/
     `PATCH`/`DELETE` on every listed resource — not just one or two examples. Use `require_auth`
     for ordinary content writes and `require_admin` for account management and privileged reports;
     leave only `GET` reads, `/login`, and health checks public. Enumerate the flagged writes from
     the audit and check each one off.
3. Keep the HTTP contract identical (same routes/methods/response shapes).

### Validation (required — Phase 3 is not done without it)

- **Install deps** in an isolated environment (venv / `npm install`).
- **Seed** the DB if the project needs it.
- **Boot** the app (in the background) and confirm it starts without errors.
- **Exercise** the original endpoints (curl / the project's `.http` file) and confirm real responses.
- **Verify the auth guard on every flagged write**: call each `POST`/`PUT`/`PATCH`/`DELETE` the
  AP-09 finding named **without** a token and confirm it returns `401` (and `403` for admin-only
  routes hit with a non-admin token); then confirm the same call **succeeds** with a valid token.
  A single unguarded write from that list means Phase 3 is not done.
- **Re-audit**: mentally (or by re-running Phase 2) confirm the corrected anti-patterns are gone.
- Shut the app down.

Then print:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<tree of src/>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

If validation fails, iterate on the refactor until the app boots and endpoints respond — do not
report success on a broken app.
