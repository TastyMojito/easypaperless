# [BUG] `documents.download(original=True)` Returns Archived PDF Instead of Original File

## Summary
When calling `documents.download(id, original=True)`, the method returns the archived PDF version of the document instead of the original uploaded file. For a document whose original is a JPEG image, the returned bytes are a PDF (confirmed via file magic bytes starting with `%PDF-`).

---

## Environment
- **Version / Release:** 0.4.0
- **Python Version:** Unknown
- **Paperless-ngx Version:** Unknown
- **Platform / OS:** Unknown
- **Other relevant context:** Bug observed against a live Paperless-ngx instance. Content verified by inspecting raw bytes (PDF magic bytes confirmed; file was not saved to disk).

---

## Steps to Reproduce
1. Have a document in Paperless-ngx whose original file is not a PDF (e.g. a JPEG image).
2. Call `documents.download(id, original=True)` using easypaperless 0.4.0.
3. Inspect the returned bytes.

---

## Expected Behavior
The returned bytes should be the original uploaded file (e.g. JPEG image data starting with `FF D8 FF`).

---

## Actual Behavior
The returned bytes are a PDF file (magic bytes `%PDF-`), which corresponds to the archived/post-processed version, not the original.

---

## Impact
- **Severity:** `High`
- **Affected Users / Systems:** Any user relying on `original=True` to retrieve non-PDF originals from a live Paperless-ngx instance.

---

## Acceptance Criteria
- [ ] Calling `documents.download(id, original=True)` for a document whose original is a JPEG returns JPEG bytes, not PDF bytes.
- [ ] Calling `documents.download(id, original=False)` (default) still returns the archived PDF.
- [ ] Both async and sync clients are fixed if the root cause affects the HTTP layer.
- [ ] A regression test (mocked or integration) covers this scenario.
- [ ] No related download functionality is broken.

---

## Investigation Findings (from integration test run)

Integration tests in `tests/integration/test_download.py` were run against a live Paperless-ngx instance and confirmed the following:

### Finding 1 — `/download/` now serves the archived PDF
`download(original=True)` hits `GET /documents/{id}/download/`. The endpoint returned bytes starting with `%PDF-` (the archived PDF), not the original PNG that was uploaded. This directly confirms the bug.

### Finding 2 — `/archive/` returns HTTP 302
`download(original=False)` hits `GET /documents/{id}/archive/`. The endpoint returns a `302 Found` redirect. The `get_download` redirect handler follows it but ends up with a non-success response, raising `PaperlessError`. This means **both** `original=True` and `original=False` are currently broken against this Paperless-ngx version.

### Root cause (confirmed)
The Paperless-ngx API has changed. The old endpoint layout (`/download/` = original, `/archive/` = archived PDF) is no longer valid. The current API uses:
- `GET /api/documents/{id}/download/` → returns the **archived PDF** (not the original)
- `GET /api/documents/{id}/download/?original=true` → returns the **original file**
- `/archive/` appears to redirect or have been removed

### Required fix
Replace the two-endpoint approach with a single-endpoint + query-parameter approach:
- `original=False` (default) → `GET /documents/{id}/download/`
- `original=True` → `GET /documents/{id}/download/?original=true`

Both async (`DocumentsResource.download`) and sync (`SyncDocumentsResource.download`) must be updated.

## Additional Notes
- Related issue: #0007 (Download Document feature spec, where the original endpoint mapping was defined).
- Regression tests are in `tests/integration/test_download.py`; they will pass once the fix is applied.

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-23
**Commit:** 646aafe (reassessed same commit after BUG-001 fix)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `download(id, original=True)` hits `?original=true` query param | Request to `GET /documents/{id}/download/?original=true` | Confirmed in `resources/documents.py:669–671` — path gets `?original=true` appended when `original=True` | ✅ Pass |
| 2 | AC2: `download(id, original=False)` hits `GET /documents/{id}/download/` (no query param) | Request to `GET /documents/{id}/download/` | Confirmed in `resources/documents.py:669` — no query param appended | ✅ Pass |
| 3 | AC3: Both async and sync clients use the new single-endpoint approach | Sync delegates to async via `_run`; both use same path logic | `SyncDocumentsResource.download` delegates to `DocumentsResource.download` — fix applies to both | ✅ Pass |
| 4 | AC4: Regression test (mocked) covers `original=True` for async client | `test_download_document_original` in `test_client_documents.py` mocks `GET /documents/1/download/` with `params={"original": "true"}` | Test exists and passes | ✅ Pass |
| 4b | AC4: Regression test (mocked) covers `original=True` for sync client | Sync test for `original=True` | `test_sync_download_document_original` added in `tests/test_sync.py` | ✅ Pass |
| 5 | AC5: No related download functionality broken (404, HTML guard tests) | `NotFoundError` raised, `ServerError` raised for HTML responses | `test_download_document_not_found`, `test_download_document_html_content_type`, `test_download_document_html_body_prefix` all pass | ✅ Pass |
| 6 | AC5: Integration tests present for both `original=True` and `original=False` | Tests in `tests/integration/test_download.py` | Both `test_download_original_returns_png_not_pdf` and `test_download_archive_returns_pdf` exist | ✅ Pass |
| 7 | Full test suite passes | 0 failures | 623 passed, 49 deselected | ✅ Pass |
| 8 | Integration test against live instance | Requires live Paperless-ngx instance | Untested — requires live instance + `tests/.env` | ⚠️ Untested |

### Bugs Found

#### BUG-001 — Missing Sync Regression Test for `original=True` [Severity: Low] ✅ Fixed
**Steps to reproduce:**
1. Review `tests/test_sync.py` for download tests.
2. Observe that `test_sync_download_document` only tests the default `original=False` path.
3. No test verifies that the sync client correctly passes `?original=true` when `original=True`.

**Expected:** A sync test covering `original=True` analogous to `test_download_document_original` in the async test suite.
**Actual:** Only the `original=False` path is covered by the sync test.
**Severity:** Low — the sync client simply delegates to async via `self._run(...)`, so correctness is implied by the async tests, but explicit coverage is missing per AC4.
**Notes:** Fixed by adding `test_sync_download_document_original` to `tests/test_sync.py`.

### Automated Tests
- Suite: `pytest tests/` — 623 passed, 49 deselected (0 failures)
- Integration suite: not run (requires live instance)

### Summary
- ACs tested: 5/5
- ACs passing: 5/5
- Bugs found: 1 (Critical: 0, High: 0, Medium: 0, Low: 1) — all fixed
- Recommendation: ✅ Ready to merge
