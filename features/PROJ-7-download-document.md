# PROJ-7: Download Document

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to download the archived (post-processed) PDF of a document so that I can work with the version paperless-ngx has optimised and OCR'd.
- As a developer, I want to download the original file that was uploaded so that I can retrieve the source file in its unmodified form.
- As a developer, I want the file returned as raw bytes so that I can save it to disk, pass it to another library, or stream it without additional processing.
- As a developer, I want a clear error when the server returns an HTML login page instead of the file so that auth misconfigurations are surfaced immediately rather than silently corrupting the download.
- As a developer, I want a `NotFoundError` when the document ID does not exist so that I can handle missing documents gracefully.

## Acceptance Criteria
- [ ] `PaperlessClient.download_document(id: int, *, original: bool = False) -> bytes` returns the raw binary content of the document file.
- [ ] When `original=False` (default), the archived/post-processed version is fetched from `GET /documents/{id}/archive/`.
- [ ] When `original=True`, the original uploaded file is fetched from `GET /documents/{id}/download/`.
- [ ] The return type is `bytes` — no decoding, no wrapping.
- [ ] Raises `NotFoundError` when the server returns HTTP 404.
- [ ] Raises `ServerError` when the response body is an HTML page (detected via `Content-Type: text/html` header or an `<!doctype` prefix in the body), indicating the server redirected to a login page instead of serving the file.
- [ ] The method is available on `SyncPaperlessClient` with the same signature (blocking wrapper).

## Edge Cases
- Document ID does not exist → raises `NotFoundError`.
- Auth token is invalid or expired: paperless-ngx may redirect to a login page rather than returning 401. This case is caught by the HTML-body detection and raises `ServerError` with a descriptive message.
- A document has no archive version (e.g. it was never processed): the API may return 404 or an error for `original=False`; this surfaces as `NotFoundError` or `ServerError` from the HTTP layer.
- The original file is not a PDF (e.g. an image or Word document): `download_document(original=True)` still returns the raw bytes regardless of format — callers are responsible for knowing the MIME type (retrievable via `get_document_metadata`).
- Large files: the entire response body is buffered into memory as `bytes`. There is no streaming API in this version.

## Technical Requirements
- The `original` flag maps to two different API endpoints: `original=True` → `/download/`, `original=False` → `/archive/`. This is an intentional paperless-ngx API design choice (not a naming error).
- HTML-response detection checks both the `Content-Type` response header and the first 9 bytes of the body (case-insensitive `<!doctype` prefix).

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
