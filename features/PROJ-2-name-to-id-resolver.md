# PROJ-2: Name-to-ID Resolver

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — uses `HttpSession.get_all_pages()` to fetch resource listings

## Overview
An internal resolver that transparently converts human-readable string names (e.g. `"Invoice"`, `"ACME Corp"`) to the integer IDs that the paperless-ngx API requires. The resolver caches full resource listings in memory and is used by `PaperlessClient` so that all public methods accept either IDs or names interchangeably.

## User Stories
- As a developer, I want to pass a tag name like `"invoice"` instead of a numeric ID so that I don't need to look up IDs beforehand.
- As a developer, I want to pass a list of tag/correspondent/document-type names in one call so that I can resolve multiple values without writing a loop.
- As a developer, I want name lookups to be case-insensitive so that `"Invoice"` and `"invoice"` both resolve to the same ID.
- As a developer, I want an already-numeric ID to pass through unchanged so that I can mix IDs and names freely in the same list.
- As a developer, I want a clear error when a name doesn't exist so that I can detect typos or stale references immediately.
- As a developer, I want the resource listing to be fetched only once per session so that repeated lookups don't cause redundant API calls.
- As a developer, I want to invalidate the cache for a specific resource so that I can force a fresh fetch after creating or renaming items.

## Acceptance Criteria

### NameResolver class (`_internal/resolvers.py`)
- [ ] `NameResolver(session)` — accepts an `HttpSession` instance; stores it as a private attribute to avoid circular imports (typed as `object` internally).
- [ ] Maintains a per-resource in-memory cache: `dict[str, dict[str, int]]` mapping resource name → `{lowercase_item_name: id}`.

### `resolve(resource, value) -> int`
- [ ] When `value` is an `int`, returns it unchanged (pass-through).
- [ ] When `value` is a `str`, ensures the resource cache is loaded, then returns the matching integer ID.
- [ ] Name matching is case-insensitive (values are lowercased before lookup).
- [ ] Raises `NotFoundError` with a message identifying the resource and the missing name when the name is not in the cache.
- [ ] Logs a DEBUG message on successful resolution: resolved resource, original name, and resulting ID.

### `resolve_list(resource, values) -> list[int]`
- [ ] Resolves each element in `values` via `resolve()` and returns a list of ints in the same order.
- [ ] Accepts mixed lists of `int` and `str`.

### Cache loading (`_ensure_loaded`)
- [ ] On the first call to `resolve()` or `resolve_list()` for a given resource, fetches all pages via `session.get_all_pages(f"/{resource}/")`.
- [ ] Builds the cache as `{item["name"].lower(): item["id"]}` from the fetched items.
- [ ] Subsequent calls for the same resource use the in-memory cache without making API requests.
- [ ] Logs DEBUG messages on cache miss (before fetch) and after cache population (count of loaded names).
- [ ] Logs DEBUG message on cache hit.

### `invalidate(resource) -> None`
- [ ] Removes the cached listing for the given resource.
- [ ] Subsequent resolution calls for that resource trigger a fresh API fetch.
- [ ] Logs a DEBUG message when a cache entry is removed.
- [ ] No-ops silently when the resource is not cached.

### Integration with PaperlessClient
- [ ] `PaperlessClient.__init__` creates a single `NameResolver` instance shared across all operations.
- [ ] `NameResolver` is not part of the public API and not re-exported from `easypaperless.__init__`.
- [ ] The following resources are resolved transparently by `PaperlessClient` methods:
  - `tags` — used in `list_documents`, `update_document`, `create_*` methods
  - `correspondents` — used in `list_documents`, `update_document`, `create_*` methods
  - `document_types` — used in `list_documents`, `update_document`, `create_*` methods
  - `storage_paths` — used in `update_document`, `create_*` methods

## Edge Cases
- **Integer pass-through** — passing an `int` to `resolve()` returns it immediately without touching the cache.
- **Mixed int/str list** — `resolve_list()` handles lists containing both integers and strings correctly.
- **Name not found** — `NotFoundError` is raised with a message that identifies both the resource and the missing name.
- **int id as str** - When the user submits an id as a str. e.g. "42" and this name does not exist - the error raised should also give a hint: "you submitted an integer as a string. ..." or similar.
- **Case sensitivity** — `"Invoice"`, `"INVOICE"`, and `"invoice"` all resolve to the same ID.
- **Cache invalidation then re-lookup** — after `invalidate(resource)`, the next call to `resolve()` triggers a full re-fetch from the API.
- **Resource with zero items** — an empty resource listing populates the cache as an empty dict; any name lookup against it raises `NotFoundError`.

## Technical Notes
- `NameResolver` is an internal class; import path is `easypaperless._internal.resolvers`.
- `HttpSession` is passed as a generic `object` to the constructor to avoid a circular import; only async methods (`get_all_pages`) are called on it at runtime.
- The cache is session-scoped (lives for the lifetime of the `PaperlessClient` instance) with no TTL or automatic expiry.

---

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
