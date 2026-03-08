# PROJ-15: Non-Document Bulk Operations

## Status: QA Passed
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to permanently delete multiple tags, correspondents, document types, or storage paths in a single request so that I can clean up resources in bulk without looping.
- As a developer, I want to set permissions and owner on multiple non-document resources at once so that I can apply access control to an entire group of tags or correspondents in one call.
- As a developer, I want a low-level escape hatch to call any bulk object operation the paperless-ngx API supports so that new operations are accessible without waiting for a high-level helper.

## Acceptance Criteria

### Low-level primitive (implemented)
- [ ] `bulk_edit_objects(object_type: str, object_ids: list[int], operation: str, **parameters) -> None` sends `POST /bulk_edit_objects/` with payload `{"objects": object_ids, "object_type": object_type, "operation": operation, ...parameters}` and returns `None` on success.
- [ ] Valid `object_type` values: `"tags"`, `"correspondents"`, `"document_types"`, `"storage_paths"`. Custom fields are **not** supported by this endpoint.
- [ ] Supported `operation` values:
  - `"delete"` — no additional parameters required.
  - `"set_permissions"` — requires a `set_permissions` object (`{"view": {"users": [], "groups": []}, "change": {"users": [], "groups": []}}`), optional `owner` (user ID or `None`), and optional `merge` (boolean, default `False`; when `True`, new permissions are merged with existing ones rather than replacing them).
- [ ] Invalid `object_type` or `operation` strings are forwarded to the API as-is; the server returns an error which propagates to the caller.

### High-level helpers (implemented)
- [ ] `bulk_delete_tags(ids: list[int]) -> None`
- [ ] `bulk_delete_correspondents(ids: list[int]) -> None`
- [ ] `bulk_delete_document_types(ids: list[int]) -> None`
- [ ] `bulk_delete_storage_paths(ids: list[int]) -> None`
- [ ] `bulk_set_permissions_tags(ids, *, set_permissions, owner, merge) -> None`
- [ ] `bulk_set_permissions_correspondents(ids, *, set_permissions, owner, merge) -> None`
- [ ] `bulk_set_permissions_document_types(ids, *, set_permissions, owner, merge) -> None`
- [ ] `bulk_set_permissions_storage_paths(ids, *, set_permissions, owner, merge) -> None`
- [ ] All high-level helpers are implemented on top of `bulk_edit_objects`.

### General
- [ ] `bulk_edit_objects` is available on `SyncPaperlessClient` with the same signature (blocking wrapper).

## Edge Cases
- Empty `object_ids` list — the request is sent as-is; the API treats it as a no-op.
- `object_type="custom_fields"` is not supported by the `bulk_edit_objects` endpoint — the server will return an error.
- `bulk_edit_objects` with `operation="delete"` on resources assigned to documents — paperless-ngx clears the relevant field on those documents; physical files are not moved.
- `set_permissions` with `merge=False` (default) replaces all existing permissions; use `merge=True` to additive-update instead of overwrite.

## Out of Scope
- Bulk operations on documents — covered by PROJ-9 (Document Bulk Operations).

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
**Date:** 2026-03-08
**Tester:** QA Engineer (Claude)
**Result:** PASS — Production-ready

### Acceptance Criteria Results

#### Low-level primitive
- [x] **AC-1**: `bulk_edit_objects()` sends `POST /bulk_edit_objects/` with correct payload structure `{"objects": ..., "object_type": ..., "operation": ..., ...parameters}` and returns `None`. **PASS** — Verified in code (`non_document_bulk.py` lines 38-44) and test `test_bulk_edit_objects`.
- [x] **AC-2**: Valid `object_type` values: `"tags"`, `"correspondents"`, `"document_types"`, `"storage_paths"`. Custom fields not supported. **PASS** — All four types used by high-level helpers; method accepts any string and forwards to API.
- [x] **AC-3**: Supported operations `"delete"` and `"set_permissions"` with correct parameter handling (`permissions` object, optional `owner`, optional `merge` with default `False`). **PASS** — Verified in both delete helpers and set_permissions helpers. `merge` defaults to `False`, `permissions` is serialised via `model_dump()`, `owner` is optional.
- [x] **AC-4**: Invalid `object_type` or `operation` strings are forwarded as-is; server error propagates. **PASS** — No client-side validation; raw strings pass through to the API payload.

#### High-level helpers
- [x] **AC-5**: `bulk_delete_tags(ids)` implemented. **PASS** — Delegates to `bulk_edit_objects("tags", ids, "delete")`.
- [x] **AC-6**: `bulk_delete_correspondents(ids)` implemented. **PASS** — Delegates to `bulk_edit_objects("correspondents", ids, "delete")`.
- [x] **AC-7**: `bulk_delete_document_types(ids)` implemented. **PASS** — Delegates to `bulk_edit_objects("document_types", ids, "delete")`.
- [x] **AC-8**: `bulk_delete_storage_paths(ids)` implemented. **PASS** — Delegates to `bulk_edit_objects("storage_paths", ids, "delete")`.
- [x] **AC-9**: `bulk_set_permissions_tags(ids, *, set_permissions, owner, merge)` implemented. **PASS** — Builds params dict and delegates to `bulk_edit_objects`.
- [x] **AC-10**: `bulk_set_permissions_correspondents(ids, *, set_permissions, owner, merge)` implemented. **PASS**.
- [x] **AC-11**: `bulk_set_permissions_document_types(ids, *, set_permissions, owner, merge)` implemented. **PASS**.
- [x] **AC-12**: `bulk_set_permissions_storage_paths(ids, *, set_permissions, owner, merge)` implemented. **PASS**.
- [x] **AC-13**: All high-level helpers are implemented on top of `bulk_edit_objects`. **PASS** — Every helper calls `self.bulk_edit_objects(...)` directly.

#### General
- [x] **AC-14**: `bulk_edit_objects` available on `SyncPaperlessClient` with same signature. **PASS** — `SyncNonDocumentBulkMixin` wraps all methods including `bulk_edit_objects` and all 8 high-level helpers.

### Edge Cases Tested
- [x] Empty `object_ids` list: request is sent as-is (no client-side guard). **PASS**.
- [x] `object_type="custom_fields"` not blocked client-side; server error propagates. **PASS**.
- [x] `set_permissions` with `merge=False` (default) replaces permissions. **PASS** — `merge` defaults to `False` in all helpers.
- [x] `set_permissions` with `merge=True` merges additively. **PASS** — `merge` parameter forwarded to payload.

### Code Quality
- Ruff lint: **PASS** (0 issues)
- Mypy strict: **PASS** (0 issues)
- All 354 tests pass (0 failures, 39 deselected integration tests)

### Observations (Low Severity)

1. **Test coverage gap — `test_bulk_edit_objects` does not assert payload**: The async test for `bulk_edit_objects` only verifies no exception is raised but does not inspect the JSON payload sent to the mock. All other bulk tests in the same file assert payload contents. Severity: **Low**. **FIXED** — payload assertion added in commit `4454b35`.

2. **Missing async tests for high-level helpers**: No async unit tests exist for `bulk_delete_tags`, `bulk_delete_correspondents`, `bulk_delete_document_types`, `bulk_delete_storage_paths`, or any `bulk_set_permissions_*` helper. Only the low-level `bulk_edit_objects` has an async test. Severity: **Low** — the helpers are trivial one-line delegations, but payload verification would increase confidence. **FIXED** — async tests added for all helpers in commit `4454b35`.

3. **Missing sync tests for most helpers**: Sync tests only cover `bulk_delete_tags` and `bulk_delete_correspondents`. Missing sync tests for `bulk_delete_document_types`, `bulk_delete_storage_paths`, `bulk_edit_objects`, and all four `bulk_set_permissions_*` wrappers. Severity: **Low** — sync wrappers are mechanical delegations. **FIXED** — all missing sync tests added in commit `4454b35`.

4. **Spec vs. implementation parameter name**: The spec said `permissions` but the implementation uses `set_permissions` (matching the project's `api-conventions.md`). Severity: **Low** — cosmetic, no functional impact. **FIXED** — spec updated to use `set_permissions`.

### Regression Testing
- Full test suite: 354 passed, 39 deselected (integration)
- PROJ-9 (Document Bulk Operations) tests: all passing
- PROJ-10 (Tags CRUD) tests: all passing
- PROJ-11 (Correspondents CRUD) tests: all passing
- Sync client tests: all passing

### Summary
| Category | Count |
|----------|-------|
| Acceptance criteria | 14/14 passed |
| Edge cases | 4/4 passed |
| Bugs (Critical/High) | 0 |
| Observations (Low) | 4 (all fixed) |

**Production-ready: YES** — All acceptance criteria pass. All 4 low-severity observations fixed in commit `4454b35`.

## Deployment
_To be added by /deploy_
