# PROJ-16: SyncPaperlessClient

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — wraps `PaperlessClient`

## User Stories
- As a script author, I want to call paperless-ngx methods synchronously so that I don't need to manage an `asyncio` event loop.
- As a REPL / shell user, I want to use `with SyncPaperlessClient(...) as client:` so that resources are cleaned up automatically.
- As a developer, I want the sync client to expose the same method signatures as `PaperlessClient` so that I can switch between them without changing call sites.
- As a developer, I want the HTTP connection pool to be reused across calls so that performance is not degraded compared to the async client.
- As a developer integrating third-party sync code, I want the sync client to forward extra constructor kwargs to the underlying async client so that all configuration options remain accessible.

## Acceptance Criteria
- [ ] `SyncPaperlessClient` is importable directly from `easypaperless`
- [ ] Constructor accepts `url`, `api_key`, and `**kwargs` forwarded to `PaperlessClient`
- [ ] Every async method on `PaperlessClient` is callable on `SyncPaperlessClient` with the same signature, blocking until the result is ready
- [ ] Non-async attributes of `PaperlessClient` are transparently proxied unchanged
- [ ] A single background event loop + daemon thread is created on `__init__` and reused for all calls (connection pool is not torn down between calls)
- [ ] `close()` method shuts down the async client, stops the event loop, joins the thread, and closes the loop
- [ ] `SyncPaperlessClient` implements the context manager protocol (`__enter__` / `__exit__`); `__exit__` calls `close()`
- [ ] No business logic lives in `SyncPaperlessClient` — it is a pure thin wrapper

## Edge Cases
- **Nested event loop (Jupyter):** Cannot be used inside a running event loop; docstring and module-level note must warn users to use `PaperlessClient` directly in those environments.
- **Exception propagation:** Exceptions raised inside the coroutine must propagate to the caller unchanged.
- **`close()` called twice:** Should not raise; loop is already stopped.
- **Kwargs forwarding:** Unknown kwargs must be passed through to `PaperlessClient`, not silently dropped.
- **New methods added to `PaperlessClient`:** The `__getattr__` proxy approach means new async methods are automatically available without updating `SyncPaperlessClient`.

## Technical Requirements
- Zero business logic in `SyncPaperlessClient` — all logic stays in `PaperlessClient`
- Background thread is a daemon thread so it does not prevent process exit if `close()` is not called
- Uses `asyncio.run_coroutine_threadsafe` + `future.result()` for blocking dispatch

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
