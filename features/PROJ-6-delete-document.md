# PROJ-6: Delete Document

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to permanently delete a document by its ID so that I can remove unwanted or duplicate documents from paperless-ngx.
- As a developer, I want a clear `NotFoundError` when the document ID does not exist so that I can distinguish a successful delete from a missing document.
- As a developer, I want the delete to return nothing on success so that I don't have to handle an unused return value.

## Acceptance Criteria
- [ ] `PaperlessClient.delete_document(id: int) -> None` sends `DELETE /documents/{id}/` and returns `None` on success (HTTP 204).
- [ ] Raises `NotFoundError` when the server returns HTTP 404.
- [ ] The method is available on `SyncPaperlessClient` with the same signature (blocking wrapper).

## Edge Cases
- Document ID does not exist → raises `NotFoundError`.
- Deleting a document is permanent and irreversible — there is no soft-delete or trash mechanism in paperless-ngx; the spec intentionally does not add one.
- Calling `delete_document` on an ID that was already deleted raises `NotFoundError` (idempotency is not guaranteed).

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
