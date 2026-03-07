# PROJ-5: Update Document

## Status: QA Passed
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping
- Requires: PROJ-2 (Name-to-ID Resolver) — for transparent string-to-ID resolution of tags, correspondent, document type, storage path
- Requires: PROJ-4 (Get Document by ID) — shares the `Document` model returned from the update response

## User Stories
- As a developer, I want to update a document's title so that I can correct or improve how it is labelled in paperless-ngx.
- As a developer, I want to reassign a document's correspondent, document type, storage path, or tags by passing a name string so that I don't have to look up numeric IDs manually.
- As a developer, I want to update only the fields I care about without touching the rest so that partial updates don't accidentally overwrite other data.
- As a developer, I want to clear a document's correspondent, document type, or storage path by passing `0` so that I can explicitly unassign those relations.
- As a developer, I want the updated `Document` returned immediately so that I can confirm the new state without a follow-up `get_document` call.
- As a developer, I want to reassign the owner of a document so that I can transfer ownership without leaving paperless-ngx.
- As a developer, I want to set view/change permissions on a document so that I can control who can access it after it has been created.
- As a developer, I want a clear `NotFoundError` when the document ID does not exist so that I can handle missing documents gracefully.

## Acceptance Criteria
- [ ] `PaperlessClient.update_document(id: int, **fields) -> Document` sends a `PATCH /documents/{id}/` request and returns the updated `Document`.
- [ ] The method accepts the following optional keyword-only fields: `title`, `content`, `date`, `correspondent`, `document_type`, `storage_path`, `tags`, `asn`, `custom_fields`, `owner`, `set_permissions`.
- [ ] Only fields that are explicitly passed (not `None`) are included in the PATCH payload — unspecified fields are left unchanged.
- [ ] `correspondent`, `document_type`, and `storage_path` accept either an integer ID or a string name; string names are resolved to IDs transparently via the name resolver.
- [ ] Passing `0` for `correspondent`, `document_type`, or `storage_path` clears the assignment (sends `0` to the API).
- [ ] `tags` accepts a list of integer IDs or string names; all names are resolved to IDs. The full list replaces the existing tag set (not a merge).
- [ ] `date` is sent to the API as the `created` field and must be an ISO-8601 date string (`"YYYY-MM-DD"`).
- [ ] `asn` is sent as `archive_serial_number`.
- [ ] `custom_fields` accepts a list of `{"field": <int>, "value": ...}` dicts and replaces the existing custom-field values.
- [ ] The returned object is a validated `Document` instance (`Document.model_validate(response_json)`).
- [ ] `owner` accepts a numeric user ID and sets the document owner. `None` leaves it unchanged.
- [ ] `set_permissions` accepts a `SetPermissions` model instance and sets view/change permissions. `None` leaves them unchanged.
- [ ] Raises `NotFoundError` when the server returns HTTP 404.
- [ ] The method is available on `SyncPaperlessClient` with the same signature (blocking wrapper).

## Edge Cases
- Calling `update_document(id)` with no keyword arguments sends an empty PATCH payload; the server returns the document unchanged.
- Passing `correspondent=0` (integer zero) must send `0` to the API to clear the field — it must not be treated as falsy and skipped.
- Passing a tag name that does not exist in paperless-ngx raises a resolver error before any HTTP request is made.
- Document ID does not exist → raises `NotFoundError`.
- `custom_fields` replaces all existing custom field values; partial updates to individual fields are not supported by this method.
- `date` is mapped to the `created` key in the payload — the parameter name differs from the wire format intentionally (follows the api-conventions naming: `date`).

## Technical Requirements
- Uses `PATCH` (not `PUT`) — only changed fields are sent.
- Name resolution for `correspondent`, `document_type`, `storage_path` uses `_resolver.resolve(resource, value)`.
- Name resolution for `tags` uses `_resolver.resolve_list("tags", values)`.
- Payload construction: iterate over each parameter; add to dict only when the value is not `None`.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
**Tested:** 2026-03-07
**Tester:** QA Engineer (Claude)
**Branch:** master (commit 31e67ec)

### Environment
- Python 3.13.12, pytest 9.0.2, respx 0.22.0, mypy (strict), ruff
- Full test suite: **340 passed**, 0 failed
- Mypy: **Success, no issues found** (38 source files)
- Coverage for `mixins/documents.py`: **94%** (10 missed lines are in unrelated `list_documents` filter branches)

### Acceptance Criteria Results

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| AC1 | `update_document` sends PATCH `/documents/{id}/` and returns `Document` | **PASS** | Code line 466; `test_update_document` |
| AC2 | Accepts all specified keyword-only fields (`title`, `content`, `date`, `correspondent`, `document_type`, `storage_path`, `tags`, `asn`, `custom_fields`, `owner`, `set_permissions`) | **PASS** | Method signature lines 400-415 |
| AC3 | Only explicitly passed fields (not `None`) included in payload | **PASS** | `test_update_document_owner_and_permissions_not_sent_when_omitted` |
| AC4 | `correspondent`, `document_type`, `storage_path` accept int ID or string name | **PASS** | `test_update_document_with_correspondent_name`, `test_update_document_document_type_with_name_resolution`, `test_update_document_storage_path_with_name_resolution` |
| AC5 | Passing `0` clears `correspondent`/`document_type`/`storage_path` | **PASS** | `test_update_document_correspondent_zero_clears`; resolver returns int 0 directly |
| AC6 | `tags` accepts list of int/str, full replacement (not merge) | **PASS** | `test_update_document_tags_with_name_resolution` |
| AC7 | `date` sent as `created` in payload | **PASS** | `test_update_document_date_mapped_to_created` |
| AC8 | `asn` sent as `archive_serial_number` | **PASS** | `test_update_document_asn_mapped_to_archive_serial_number` |
| AC9 | `custom_fields` accepts list of dicts, replaces existing | **PASS** | `test_update_document_custom_fields_sent_in_payload` |
| AC10 | Returned object is validated `Document` instance | **PASS** | `Document.model_validate(resp.json())` at line 467 |
| AC11 | `owner` accepts numeric user ID | **PASS** | `test_update_document_with_owner` |
| AC12 | `set_permissions` accepts `SetPermissions` model | **PASS** | `test_update_document_with_set_permissions` |
| AC13 | Raises `NotFoundError` on HTTP 404 | **PASS** | `test_update_document_not_found` |
| AC14 | Available on `SyncPaperlessClient` with same signature | **PASS** | `sync_mixins/documents.py` lines 119-148; `test_sync_update_document` |

### Edge Cases

| Edge Case | Result | Evidence |
|-----------|--------|----------|
| No kwargs sends empty PATCH payload | **PASS** | `test_update_document_empty_kwargs_sends_empty_body` |
| `correspondent=0` not treated as falsy | **PASS** | `test_update_document_correspondent_zero_clears` |
| Nonexistent tag name raises resolver error before HTTP | **PASS** | `test_update_document_nonexistent_tag_name_raises_resolver_error` |
| Document ID not found raises `NotFoundError` | **PASS** | `test_update_document_not_found` |

### Regression Testing
- Full test suite (340 tests): all passing
- Type checking (mypy strict): clean
- Related features (PROJ-1 HTTP core, PROJ-2 resolver, PROJ-4 get_document): no regressions

### Bugs Found
**None.**

### Test Coverage Observations (non-blocking)
- No dedicated test for `update_document(id, content="...")` — the `content` field follows the identical pattern as `title` (simple string pass-through), so this is cosmetic only.
- No dedicated tests for `document_type=0` or `storage_path=0` clearing — same code path as `correspondent=0` (resolver returns int directly).
- Ruff warnings exist in `scripts/cli.py` and test files (unused imports, line length) but are pre-existing and unrelated to PROJ-5.

### Production-Ready Decision
**READY** — All 14 acceptance criteria pass, all documented edge cases pass, no bugs found, no regressions. Zero Critical or High issues.

## Deployment
_To be added by /deploy_
