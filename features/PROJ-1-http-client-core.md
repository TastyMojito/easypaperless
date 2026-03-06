# PROJ-1: HTTP Client Core

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- None

## Overview
Internal HTTP session with token authentication, error mapping, pagination, and a structured exception hierarchy. This is the foundation all other features build on.

## User Stories
- As a developer, I want to instantiate a client with a base URL and API key so that I don't have to manage authentication headers manually.
- As a developer, I want HTTP errors mapped to typed Python exceptions so that I can handle auth failures, not-found cases, and server errors distinctly in my code.
- As a developer, I want paginated list endpoints to be automatically traversed so that I don't have to implement pagination logic myself.
- As a developer, I want to configure a default request timeout at construction time so that I can tune the client for slow or fast server environments.
- As a developer, I want binary downloads to work correctly even when the server issues cross-host redirects so that file downloads don't silently fail or return wrong content.

## Acceptance Criteria

### HttpSession
- [ ] `HttpSession(base_url, api_key, timeout=30.0)` — `timeout` is configurable at construction; defaults to 30 seconds.
- [ ] Base URL is normalized: trailing slashes stripped, `/api` appended.
- [ ] All requests include `Authorization: Token {api_key}` header.
- [ ] `close()` closes the underlying HTTP connection pool.
- [ ] `request(method, path, *, params, json, data, files, timeout)` — generic request; per-call `timeout` overrides the session default.
- [ ] Convenience methods: `get()`, `post()`, `patch()`, `delete()`.
- [ ] `post()` exposes a `timeout` parameter (for long-running operations like uploads).
- [ ] `get_download()` follows redirects manually, re-attaching the `Authorization` header on each hop (up to 5 hops).
- [ ] `get_all_pages(path, params, *, max_results, on_page)` — fetches all pages of a paginated list endpoint, optionally capped at `max_results`; calls `on_page(fetched_so_far, total_count)` after each page.

### Exception Hierarchy
- [ ] `PaperlessError(message, status_code=None)` — base exception; all easypaperless exceptions inherit from it.
- [ ] `AuthError` — raised on 401 or 403 responses.
- [ ] `NotFoundError` — raised on 404 responses.
- [ ] `ValidationError` — raised on 422 responses.
- [ ] `ServerError` — raised on 5xx responses and on transport-level errors (timeouts, connection failures).
- [ ] `UploadError` — raised when a document processing task reports a `FAILURE` status.
- [ ] `TaskTimeoutError` — raised when upload polling exceeds the configured timeout; `status_code` is always `None`.
- [ ] All exceptions carry the originating HTTP status code where applicable.

## Edge Cases
- **Trailing slash in base URL** — must be stripped before `/api` is appended to avoid double-slash paths.
- **Non-JSON error responses** — `_raise_for_status` falls back to raw response text if the body is not valid JSON.
- **Redirect strips auth header** — `get_download()` handles cross-host redirects by manually re-issuing each hop rather than relying on httpx's built-in redirect follower.
- **Redirect loop** — `get_download()` aborts after 5 hops to prevent infinite loops.
- **Transport errors** — `httpx.TimeoutException` and `httpx.HTTPError` are caught and re-raised as `ServerError` with a descriptive message.
- **max_results across pages** — `get_all_pages()` truncates results to exactly `max_results` even when the last fetched page contains extra items.
- **per-call timeout on post** — individual calls (e.g. upload) can override the session-level timeout via the `timeout` parameter on `post()`.

## Technical Notes
- HTTP client: `httpx` (async-first; `httpx.AsyncClient` used internally).
- `HttpSession` is an internal class (`_internal/http.py`); not part of the public API.
- Exceptions (`exceptions.py`) are public and re-exported from `easypaperless.__init__`.

---

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
