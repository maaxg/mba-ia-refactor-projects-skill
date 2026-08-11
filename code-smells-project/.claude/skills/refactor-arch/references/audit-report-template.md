# Reference: Audit Report Template (Phase 2)

The Phase 2 report MUST follow this exact structure. Save it to the requested path
(e.g. `reports/audit-project-N.md`) and also print the summary block to the console.

Rules:
- Findings sorted **CRITICAL → HIGH → MEDIUM → LOW**.
- Every finding has an exact `file:line` (or line range). No invented lines.
- The `Summary` counts must match the number of findings listed.
- Include a note for any dangerous endpoint you plan to remove/lock down in Phase 3.

---

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project-name>
Stack:   <language> + <framework version>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <YYYY-MM-DD>

## Summary
CRITICAL: <c> | HIGH: <h> | MEDIUM: <m> | LOW: <l>
Total: <total> findings

## Findings

### [CRITICAL] <Anti-pattern title>  (AP-XX)
- **File:** `<path>:<line-or-range>`
- **Description:** <what the code does wrong, concretely>
- **Impact:** <why it matters — security / correctness / maintainability>
- **Recommendation:** <the fix, referencing the target MVC layer / playbook pattern>

### [CRITICAL] <next finding> (AP-XX)
...

### [HIGH] <finding> (AP-XX)
...

### [MEDIUM] <finding> (AP-XX)
...

### [LOW] <finding> (AP-XX)
...

## Deprecated APIs
<explicit list of deprecated API usages found, or "None detected for the target runtime version">

## Endpoints preserved / changed in Phase 3
- Preserved (same URL/method/response): <list>
- Removed or locked down (with justification): <list, e.g. POST /admin/query — arbitrary SQL execution>

================================
Total: <total> findings
================================
```

---

## Console summary (print after saving the file)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project-name>
Stack:   <language> + <framework>
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: <c> | HIGH: <h> | MEDIUM: <m> | LOW: <l>

Findings
[CRITICAL] <title> — <file>:<line>
[CRITICAL] <title> — <file>:<line>
[HIGH] <title> — <file>:<line>
... (all findings, one line each, severity-ordered)

================================
Total: <total> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
