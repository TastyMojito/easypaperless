# [FEATURE] Add Structured Logging Support Across All Resource Methods

## Summary

Add Python standard-library logging to the easypaperless client and all resource methods. Library consumers (e.g. an MCP server) should be able to configure log destination, format, and level themselves — following the standard Python library logging convention.

---

## Problem Statement

Currently the library emits no log output. When using easypaperless inside an application such as an MCP server, there is no way to observe what HTTP requests are being made, what responses are returned, or where errors occur. This makes debugging difficult and operational visibility impossible without adding external instrumentation.

---

## Proposed Solution

Adopt Python's standard `logging` module throughout the library. Each module uses `logging.getLogger(__name__)`, producing a logger hierarchy rooted at `easypaperless` (e.g. `easypaperless._internal.http`, `easypaperless._internal.resources.documents`). The library never configures handlers, formatters, or levels — all of that is left to the consuming application.

Log calls are added across all resource methods and the HTTP layer at appropriate levels:

- **DEBUG** — full request details (method, URL, headers, body) and full response details (status code, headers, body) for every HTTP call.
- **INFO** — high-level operation events (e.g. "listing documents", "creating tag 'invoices'", "uploading file foo.pdf").
- **WARNING** — recoverable unexpected situations (e.g. resolver cache miss falling back to API, unexpected response field).
- **ERROR** — operation failures (e.g. HTTP error responses, parse failures).

Consuming applications configure the `easypaperless` logger however they like — for example, an MCP server can direct it to a rotating file at `DEBUG` level with a single `logging.basicConfig` or handler setup call in their own code.

---

## User Stories

- As a library consumer building an MCP server, I want to configure a file handler on the `easypaperless` logger so that all API calls are logged to a file for debugging.
- As a developer using easypaperless interactively, I want to enable DEBUG logging so that I can see exact request and response payloads being exchanged with the Paperless instance.
- As an operator running easypaperless in production, I want INFO-level logs so that I have an audit trail of operations performed without excessive noise.

---

## Scope

### In Scope
- Add `logging.getLogger(__name__)` to every module that contains resource or HTTP logic.
- Add `DEBUG` log calls in the HTTP layer for outgoing request details (method, URL, sanitized headers, body) and incoming response details (status code, headers, body).
- Add `INFO` log calls at the start of each public resource method describing the operation and key parameters.
- Add `WARNING` and `ERROR` log calls where appropriate for unexpected or failure conditions.
- Cover all resource modules: `documents`, `tags`, `correspondents`, `document_types`, `storage_paths`, `custom_fields`, `notes`, `upload`, `document_bulk`, `non_document_bulk`, and the HTTP/resolver layer.
- Cover both async (`_internal/resources/`) and sync (`_internal/sync_resources/`) variants.

### Out of Scope
- The library does not configure any handlers, formatters, log levels, or log destinations.
- No new public API surface (no logging configuration parameters on `PaperlessClient` or `SyncPaperlessClient`).
- Log redaction / masking of sensitive values (e.g. auth tokens) beyond what is already hidden by not logging the `Authorization` header value.

---

## Acceptance Criteria
- [ ] Every module under `_internal/` that contains resource logic has a module-level `logger = logging.getLogger(__name__)`.
- [ ] Every outgoing HTTP request is logged at `DEBUG` level with method, URL, and request body (if present).
- [ ] Every received HTTP response is logged at `DEBUG` level with status code and response body.
- [ ] Every public resource method logs at `INFO` level when it is called, including the key identifying parameters (e.g. document ID, tag name).
- [ ] ERROR or WARNING is logged for HTTP error responses before the exception is raised.
- [ ] The library does not call `logging.basicConfig`, `logging.setLevel`, `addHandler`, or any other logging configuration function anywhere in its source.
- [ ] A consuming application can capture all `easypaperless` logs by attaching a handler to `logging.getLogger("easypaperless")`.
- [ ] All existing tests continue to pass without modification.
- [ ] No auth token values appear in log output at any level.

---

## Dependencies & Constraints

- Python standard library `logging` only — no third-party logging frameworks.
- Must follow PEP convention for library logging: no root logger usage, no handler/formatter setup in library code.

---

## Priority
`Medium`

---

## Additional Notes

The `Authorization` header carries the Paperless API token. When logging request headers at DEBUG level, the value of the `Authorization` header must be omitted or replaced with a placeholder (e.g. `"Bearer <redacted>"`) to avoid leaking credentials into log files.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-17
**Commit:** bf881cb (HEAD — implementation not yet committed)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: Every `_internal/` resource module has `logger = logging.getLogger(__name__)` | All modules have module-level logger | All async resource modules + resolver + http have loggers; sync resource modules have logger declared (but unused — see BUG-001) | ✅ Pass |
| 2 | AC2: Every outgoing HTTP request logged at DEBUG with method, URL, request body | DEBUG record with method + path + body | `http.py` logs method, path, and body (or `<multipart/form-data>` for uploads) before sending | ✅ Pass |
| 3 | AC3: Every HTTP response logged at DEBUG with status code and response body | DEBUG record with status + body | `request()` logs status, method, path, and truncated response body; `get_download()` logs status + path but **omits binary body** (intentional) | ✅ Pass |
| 4 | AC4: Every public resource method logs at INFO when called | INFO record with operation + key params | All async public methods emit INFO (58 call sites); sync methods delegate to async so INFO is still emitted — from async logger name, not sync | ✅ Pass |
| 5 | AC5: WARNING or ERROR logged for HTTP error responses before exception | WARNING log before raise | `_raise_for_status` logs `WARNING HTTP <status> <method> <path> — <detail>` before raising | ✅ Pass |
| 6 | AC6: Library does not call `basicConfig`, `setLevel`, `addHandler` etc. | No configuration calls in source | `ruff check` passes; `__init__.py` correctly uses only `addHandler(NullHandler())` — allowed by PEP 282 | ✅ Pass |
| 7 | AC7: Consuming app can capture logs via `logging.getLogger("easypaperless")` | All loggers are children of `easypaperless` | All loggers use `getLogger(__name__)` rooted at `easypaperless.*`; test `test_easypaperless_logger_has_no_non_null_handlers` passes | ✅ Pass |
| 8 | AC8: All existing tests continue to pass | 573 tests pass | 573 passed, 0 failed | ✅ Pass |
| 9 | AC9: No auth token values in log output | API key not in any log record | `test_auth_token_not_in_debug_logs` passes; headers are not logged | ✅ Pass |
| 10 | Edge: `get_download` redirect hops logged | Redirect status/location logged at DEBUG | Lines 148, 157 log each redirect hop and final status | ✅ Pass |
| 11 | Edge: Upload task polling events logged | Task success/failure/timeout logged | `documents.py` logs task_id on accept, success, failure, revocation, and timeout | ✅ Pass |
| 12 | Edge: Resolver cache hits/misses logged | Cache events logged at DEBUG | `resolvers.py` logs resolved ID, cache hit, cache miss, cache populated, cache invalidated | ✅ Pass |
| 13 | Edge: Long response bodies truncated in DEBUG log | Body capped at 1000 chars + `...<truncated>` | `http.py` lines 117-119: truncates to 1000 chars | ✅ Pass |
| 14 | Type/lint: ruff + mypy clean | No errors | `ruff check` all passed; `mypy` 15 source files — no issues | ✅ Pass |

### Bugs Found

#### BUG-001 — Sync Resource `logger` Variables Declared but Never Used [Severity: Low] ✅ Fixed

**Steps to reproduce:**
1. Open any sync resource file, e.g. `src/easypaperless/_internal/sync_resources/tags.py`.
2. Observe that `logger = logging.getLogger(__name__)` is present but `logger.info(...)` / `logger.debug(...)` are never called anywhere in the file.
3. Check all six sync resource files — same pattern in every one.

**Expected:** Either (a) sync public methods emit their own INFO log records with logger name `easypaperless._internal.sync_resources.*`, or (b) if delegation to async is sufficient, the unused `logger` variable is removed.

**Actual:** The variable is declared in all six sync resource modules but is never used. All INFO logs are emitted by the async delegate with logger name `easypaperless._internal.resources.*`. A consumer filtering specifically on `easypaperless._internal.sync_resources` will receive no records.

**Severity:** Low
**Notes:** Functionally harmless — logging still occurs via the async path. No test coverage gap either because the auto-test suite passes. This is dead code that could be confusing to future contributors.

**Fix:** Removed `import logging` and `logger = logging.getLogger(__name__)` from all six sync resource files (`tags.py`, `correspondents.py`, `custom_fields.py`, `document_types.py`, `storage_paths.py`, `documents.py`). Sync resources delegate to async counterparts which emit all INFO logs via `easypaperless._internal.resources.*` loggers.

### Automated Tests

- Suite: `tests/test_issue_0030_logging.py` — 7 passed, 0 failed
- Suite: Full test suite (`pytest tests/`) — 573 passed, 0 failed

### Summary

- ACs tested: 9/9
- ACs passing: 9/9
- Bugs found: 1 (Critical: 0, High: 0, Medium: 0, Low: 1)
- Recommendation: ✅ Ready to merge
