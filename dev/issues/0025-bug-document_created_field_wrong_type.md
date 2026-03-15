# [BUG] `Document.created` Typed as `datetime` Instead of `date`

## Summary

The `created` field on the `Document` model is typed as `datetime`, but paperless-ngx API v9 changed this field to a plain `date`. As a result, parsing any document response raises a validation error because Pydantic cannot coerce a date string (e.g. `"2024-01-15"`) into `datetime`. The `created_date` field (which duplicated the date portion) is now deprecated by paperless-ngx and will be removed in a future API version.

---

## Environment
- **Version / Release:** easypaperless 0.2.0
- **Python Version:** 3.11+
- **Paperless-ngx Version:** v9+ (API change introduced in v9)
- **Platform / OS:** Any
- **Other relevant context:** Discovered while building an MCP server on top of easypaperless. `get_document` and `update_document` both fail with a Pydantic validation error when paperless-ngx returns a date-only string for `created`.

---

## Steps to Reproduce
1. Connect to a paperless-ngx instance running API v9 or later.
2. Call `client.documents.get(id=<any_document_id>)`.
3. Observe a Pydantic `ValidationError` for the `created` field.

---

## Expected Behavior

`Document.created` is typed as `date` (not `datetime`), matching the paperless-ngx v9 API contract. Parsing succeeds and the returned `Document` object has a `date` value in `created`.

---

## Actual Behavior

Pydantic raises a `ValidationError` because the API returns a date string (e.g. `"2024-01-15"`) for `created`, which cannot be parsed as `datetime`. Any method that returns a `Document` object (get, list, update) is broken on v9+ instances.

---

## Impact
- **Severity:** `High`
- **Affected Users / Systems:** All users on paperless-ngx API v9+. Core document retrieval and update operations fail.

---

## Acceptance Criteria
- [x] `Document.created` is typed as `date | None` in `src/easypaperless/models/documents.py`.
- [x] `Document.created_date` is marked as deprecated (e.g. via a docstring note) since paperless-ngx will remove it in a future version.
- [x] The `created` field is correctly typed as `date` in all `update_document` / `edit_document` method signatures that accept it as input.
- [x] Existing unit tests for document parsing are updated to use date values for `created`.
- [x] A regression test verifies that a document response with a date-only `created` field parses without error.
- [x] No other document fields are inadvertently affected.

---

## Additional Notes

Paperless-ngx changelog (Version 9):
> The document `created` field is now a date, not a datetime. The `created_date` field is considered deprecated and will be removed in a future version.

Root cause: `src/easypaperless/models/documents.py` line 204 — `created: datetime | None = None` should be `created: date | None = None`.
Also check update/edit input models and any mixin method signatures that reference `created` with a `datetime` annotation.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 9db1cd1 (changes are in working copy, not yet committed)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `Document.created` typed as `date \| None` | `date \| None` annotation at models/documents.py:207 | `created: date \| None = None` confirmed | ✅ Pass |
| 2 | AC2: `Document.created_date` deprecated in docstring | Deprecation note in `Document` docstring | `**Deprecated** by paperless-ngx as of v9 — use created instead. Will be removed in a future API version.` | ✅ Pass |
| 3 | AC3: `created` typed as `date` in `update()` signatures (async + sync) | `date \| str \| None \| _Unset` in both resources | Confirmed in `_internal/resources/documents.py:447` and `_internal/sync_resources/documents.py:185` | ✅ Pass |
| 4 | AC4: Existing test updated to use date value for `created` | `test_document_created_is_datetime` replaced with `test_document_created_is_date` | Replaced; new test uses `"2024-03-15"` (date string) and asserts `isinstance(doc.created, date)` and `not isinstance(doc.created, datetime)` | ✅ Pass |
| 5 | AC5: Regression test — date-only string parses without error | `Document.model_validate({"id":1,"title":"T","created":"2024-01-15"})` succeeds and returns `date(2024,1,15)` | `test_document_created_date_only_string_parses_without_error` passes | ✅ Pass |
| 6 | AC6: No other document fields inadvertently affected | `modified`, `added` remain `datetime`; `created_date` remains `date` | Confirmed — only `Document.created` annotation changed | ✅ Pass |
| 7 | Edge: `created=None` parses without error | `doc.created is None` | Confirmed via manual test | ✅ Pass |
| 8 | Edge: `date` object passed directly to `Document.model_validate` | Accepts `date(2024,3,15)` | Confirmed via manual test | ✅ Pass |
| 9 | Edge: midnight datetime string `"2024-03-15T00:00:00Z"` | Pydantic accepts exact-date datetimes; result is `date(2024,3,15)` | Confirmed — Pydantic coerces to `date` | ✅ Pass |
| 10 | Edge: non-midnight datetime string `"2024-03-15T10:00:00Z"` | Validation error (new strict behaviour, by design) | `ValidationError: Datetimes provided to dates should have zero time` | ✅ Pass (expected; pre-v9 datetime strings with non-zero time are now rejected — see note below) |
| 11 | `update()` sends `created` as ISO-8601 date string | PATCH body contains `"created": "2024-06-15"` | `test_update_document_created_sent_as_created` passes | ✅ Pass |
| 12 | `update()` accepts `date` object and formats it | PATCH body contains `"created": "2024-06-15"` when `date(2024,6,15)` passed | `test_update_document_created_accepts_date_object` passes | ✅ Pass |
| 13 | Full test suite — no regressions | All 499 tests pass | 499 passed, 0 failed | ✅ Pass |
| 14 | mypy strict type check | No type errors | `Success: no issues found in 32 source files` | ✅ Pass |
| 15 | ruff lint/format — changed files | No new lint errors in changed files | 16 ruff errors found, all in pre-existing unrelated files (`client.py`, `sync.py` docstrings, integration tests, upload test) — zero errors in `models/documents.py` or `tests/test_models.py` | ✅ Pass |

### Bugs Found

None.

> **Note on edge case #10:** Non-midnight datetime strings (e.g. `"2024-03-15T10:00:00Z"`) now raise a `ValidationError` for `Document.created`. This is a deliberate breaking change for users on pre-v9 paperless-ngx instances that returned full datetimes. The issue explicitly targets v9+ compatibility. No action required, but worth documenting for the changelog.

### Automated Tests
- Suite: `pytest tests/` (excluding integration) — **499 passed, 0 failed**
- mypy: **0 issues**
- ruff: 16 pre-existing errors in unrelated files; **0 new errors** introduced by this change

### Summary
- ACs tested: 6/6
- ACs passing: 6/6
- Bugs found: 0
- Recommendation: ✅ Ready to merge
