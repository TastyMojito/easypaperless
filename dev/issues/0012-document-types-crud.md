# PROJ-12: Document Types CRUD

## Status: QA Passed
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to list all document types so that I can inspect the taxonomy defined in my paperless-ngx instance.
- As a developer, I want to filter document types by name substring so that I can find one without loading the full list.
- As a developer, I want to fetch a single document type by ID so that I can read its properties.
- As a developer, I want to create a new document type with name, auto-match settings, and permissions so that I can manage the taxonomy programmatically.
- As a developer, I want to update an existing document type so that I can rename it or adjust its auto-match rules.
- As a developer, I want to delete a document type so that I can remove unused types without using the web UI.

## Acceptance Criteria

### list_document_types
- [x] `list_document_types(*, ids, name_contains, page, page_size, ordering, descending) -> list[DocumentType]` fetches `GET /document_types/` and returns validated `DocumentType` instances.
- [x] `ids` filters to only document types whose ID is in the list (`id__in` query param).
- [x] `name_contains` does a case-insensitive substring match on document type name (`name__icontains`).
- [x] When `page` is omitted, all pages are fetched automatically (auto-pagination).
- [x] When `page` is set, only that page is returned (disables auto-pagination).
- [x] `ordering` + `descending` control sort order; `descending=True` prepends `-` to the field name.

### get_document_type
- [x] `get_document_type(id: int) -> DocumentType` fetches `GET /document_types/{id}/` and returns a validated `DocumentType`.
- [x] Raises `NotFoundError` on HTTP 404.

### create_document_type
- [x] `create_document_type(*, name, match, matching_algorithm, is_insensitive, owner, set_permissions) -> DocumentType` sends `POST /document_types/` and returns the created `DocumentType`.
- [x] `name` is required; all other fields are optional.
- [x] `matching_algorithm` integer values: `0`=none, `1`=any word, `2`=all words, `3`=exact, `4`=regex, `5`=fuzzy, `6`=auto (ML).
- [x] `owner` sets the owning user ID; `None` leaves the document type without an owner.
- [x] `set_permissions` sets explicit view/change permissions via `SetPermissions` model.

### update_document_type
- [x] `update_document_type(id: int, *, name, match, matching_algorithm, is_insensitive) -> DocumentType` sends `PATCH /document_types/{id}/` and returns the updated `DocumentType`.
- [x] Only fields explicitly passed (not `None`) are included in the payload.
- [x] Raises `NotFoundError` on HTTP 404.
- [x] `owner` and `set_permissions` are **not yet supported** in `update_document_type` (planned — consistent with the same gap in `update_document`, `update_tag`, and `update_correspondent`).

### delete_document_type
- [x] `delete_document_type(id: int) -> None` sends `DELETE /document_types/{id}/` and returns `None` on success.
- [x] Raises `NotFoundError` on HTTP 404.

### General
- [x] The `DocumentType` model exposes: `id`, `name`, `slug`, `match`, `matching_algorithm`, `is_insensitive`, `document_count`, `owner`, `user_can_change`.
- [x] All methods are available on `SyncPaperlessClient` with the same signatures (blocking wrapper).

## Edge Cases
- Creating a document type with a name that already exists → server returns an error (likely HTTP 400); propagated as-is.
- Deleting a document type that is assigned to documents — paperless-ngx clears the `document_type` field on those documents; no error is raised.
- `update_document_type` called with no keyword arguments → empty PATCH payload; server returns the document type unchanged.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
**QA Date:** 2026-03-08
**Tested by:** QA Engineer (Claude)
**Test Suite:** 354 tests passing (full suite), 19 document-type-specific async tests, 5 sync tests
**Coverage:** 100% async mixin, 100% model, 94% sync mixin (1 uncovered statement)
**Mypy:** Clean (0 errors)
**Ruff:** Clean (0 violations)

### Acceptance Criteria Results

#### list_document_types
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Signature + GET /document_types/ + returns DocumentType | PASS | `test_list_document_types` |
| 2 | `ids` -> `id__in` query param | PASS | `test_list_document_types_ids` |
| 3 | `name_contains` -> `name__icontains` | PASS | `test_list_document_types_name_contains` |
| 4 | Auto-pagination when `page` omitted | PASS | `test_list_document_types` uses `get_all_pages` path |
| 5 | Single page when `page` set | PASS | `test_list_document_types_page_size_ordering` verifies `page=3` |
| 6 | `ordering` + `descending` | PASS | Code verified; `descending=True` prepends `-`. Tested via storage paths pattern (shared implementation). |

#### get_document_type
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | GET /document_types/{id}/ returns DocumentType | PASS | `test_get_document_type` |
| 2 | Raises NotFoundError on 404 | PASS | `test_get_document_type_not_found` |

#### create_document_type
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | POST /document_types/ returns DocumentType | PASS | `test_create_document_type` |
| 2 | `name` required, others optional | PASS | Signature enforces `name` as keyword-only, no default |
| 3 | `matching_algorithm` integer enum | PASS | `test_create_document_type_all_params` sends `matching_algorithm=3` |
| 4 | `owner` sets owning user ID | PASS | `test_create_document_type_all_params` verifies `owner=1` in payload |
| 5 | `set_permissions` via SetPermissions | PASS | `test_create_document_type_all_params` verifies permission structure |

#### update_document_type
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | PATCH /document_types/{id}/ returns DocumentType | PASS | `test_update_document_type` |
| 2 | Only non-None fields in payload | PASS | `test_update_document_type_only_sends_provided_fields` |
| 3 | Raises NotFoundError on 404 | PASS | `test_update_document_type_not_found` |
| 4 | `owner`/`set_permissions` not supported | PASS | Verified: not in signature |

#### delete_document_type
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | DELETE /document_types/{id}/ returns None | PASS | `test_delete_document_type` |
| 2 | Raises NotFoundError on 404 | PASS | `test_delete_document_type_not_found` |

#### General
| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Model fields: id, name, slug, match, matching_algorithm, is_insensitive, document_count, owner, user_can_change | PASS | `test_document_type_model_all_fields` verifies all 9 fields |
| 2 | All methods on SyncPaperlessClient | PASS | Sync tests for list, get, create, delete all pass |

### Edge Cases
| Edge Case | Result | Evidence |
|-----------|--------|----------|
| Empty PATCH (no kwargs) | PASS | `test_update_document_type_empty_patch` sends `{}` |
| Cache invalidation on create | PASS | `test_create_document_type_invalidates_cache` |
| Cache invalidation on update | PASS | `test_update_document_type_invalidates_cache` |
| Cache invalidation on delete | PASS | `test_delete_document_type_invalidates_cache` |

### Observations (Low Severity)

1. **Missing sync `update_document_type` test** (Low)
   - Tags and correspondents both have `test_sync_update_tag` / `test_sync_update_correspondent`, but there is no `test_sync_update_document_type`. The sync mixin code exists and is correct (verified by code review), but this leaves one uncovered line in `sync_mixins/document_types.py` (94% vs 100%). **FIXED** — `test_sync_update_document_type` added in commit `4454b35`.

2. **No dedicated `descending=True` test for document types** (Low)
   - `test_list_document_types_page_size_ordering` tests `ordering="id"` but not `descending=True`. The storage paths test covers this pattern, and the code is identical via shared `_list_resource`, so the risk is negligible. **FIXED** — `test_list_document_types_descending` added in commit `4454b35`.

### Regression Testing
- Full test suite: **354 passed**, 0 failed
- No regressions detected in any feature area

### Security Audit
- No credential exposure in tests or implementation
- No user-controlled format strings
- `extra="ignore"` on models prevents unexpected field injection
- API key handled by existing `HttpSession` (PROJ-1, QA Passed)

### Production-Ready Recommendation
**READY** — All 20 acceptance criteria pass. No Critical or High bugs. Two Low-severity observations fixed in commit `4454b35`.

## Deployment
_To be added by /deploy_
