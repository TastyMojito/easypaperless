# PROJ-8: Upload Document

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated multipart HTTP requests and error mapping
- Requires: PROJ-2 (Name-to-ID Resolver) — for transparent string-to-ID resolution of tags, correspondent, document type, storage path
- Requires: PROJ-4 (Get Document by ID) — used internally to fetch the resulting `Document` after task completion when `wait=True`

## User Stories
- As a developer, I want to upload a file to paperless-ngx by providing a file path so that I can ingest documents programmatically without using the web UI.
- As a developer, I want to pre-assign metadata (title, date, correspondent, document type, storage path, tags, ASN) at upload time so that newly ingested documents are organised without a follow-up update call.
- As a developer, I want to get back a task ID immediately (fire-and-forget) so that I can submit many uploads concurrently without blocking on processing.
- As a developer, I want to optionally wait for processing to complete and receive the resulting `Document` in a single call so that I don't have to implement polling logic myself.
- As a developer, I want a descriptive error when processing fails so that I can surface the paperless-ngx failure reason to my own application.
- As a developer, I want a timeout error when processing takes too long so that my application does not hang indefinitely.

## Acceptance Criteria
- [ ] `PaperlessClient.upload_document(file, **metadata) -> str | Document` sends a multipart POST to `POST /documents/post_document/` and returns a Celery task ID string by default.
- [ ] `file` accepts a `str` or `pathlib.Path` pointing to a local file. The file is read from disk and sent as the `document` form field along with its filename.
- [ ] The following optional keyword-only metadata fields are supported: `title`, `created` (ISO-8601 date string), `correspondent` (ID or name), `document_type` (ID or name), `storage_path` (ID or name), `tags` (list of IDs or names), `asn` (integer archive serial number).
- [ ] `correspondent`, `document_type`, `storage_path`, and `tags` accept string names which are resolved to IDs transparently before upload.
- [ ] Only metadata fields that are explicitly passed (not `None`) are included in the multipart payload.
- [ ] When `wait=False` (default), the method returns immediately with the task ID string (the raw UUID returned by paperless-ngx, stripped of surrounding quotes).
- [ ] When `wait=True`, the method polls `GET /api/tasks/?task_id=<id>` at `poll_interval` second intervals until the task reaches a terminal state or the timeout is exceeded.
- [ ] When `wait=True` and the task succeeds, the method returns the fully processed `Document` fetched via `get_document(document_id)`.
- [ ] When `wait=True` and the task fails, raises `UploadError` with the paperless-ngx failure message.
- [ ] When `wait=True` and processing does not complete within `poll_timeout` seconds, raises `TaskTimeoutError`.
- [ ] `poll_interval` and `poll_timeout` can be overridden per call (keyword arguments); they fall back to client-level defaults when omitted.
- [ ] The method is available on `SyncPaperlessClient` with the same signature (blocking wrapper).

## Edge Cases
- File path does not exist or is not readable → raises a standard Python `FileNotFoundError` before any HTTP request is made.
- Paperless-ngx rejects the upload (e.g. unsupported file type) → the task transitions to `FAILURE`; if `wait=True` this raises `UploadError`; if `wait=False` the caller receives the task ID and must poll manually to discover the failure.
- `wait=True` with a very short `poll_timeout` → raises `TaskTimeoutError`; the document may still be processed successfully on the server side.
- The task status endpoint returns an empty list before the task is registered → the poller continues sleeping and retrying until the task appears or the timeout is exceeded.
- Passing a tag name that does not exist in paperless-ngx raises a resolver error before any HTTP request is made.
- `created` is passed directly to the API as-is; no date validation is performed by the client — invalid strings will be rejected by the server.

## Technical Requirements
- Upload uses multipart form encoding (`files={"document": (filename, bytes)}`), not JSON.
- The task ID is returned as a plain string from the API response body (JSON-encoded string); outer quotes must be stripped.
- Polling state machine: `PENDING` / `STARTED` / `RETRY` → keep polling; `SUCCESS` → fetch document and return; `FAILURE` → raise `UploadError`; timeout → raise `TaskTimeoutError`.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
