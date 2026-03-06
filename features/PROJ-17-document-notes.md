# PROJ-17: Document Notes

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping
- Requires: PROJ-4 (Get Document) — notes are a sub-resource of documents

## User Stories
- As a developer, I want to list all notes on a document so that I can read annotations left by users.
- As a developer, I want to create a note on a document so that I can programmatically annotate documents.
- As a developer, I want to delete a note from a document so that I can remove outdated or incorrect annotations.

## Acceptance Criteria

### get_notes
- [ ] `get_notes(document_id: int) -> list[DocumentNote]` sends `GET /documents/{document_id}/notes/` and returns a validated list of `DocumentNote` instances.
- [ ] Returns an empty list when the document has no notes.
- [ ] Raises `NotFoundError` when the document does not exist (HTTP 404).
- [ ] Notes are returned in the order provided by the server (creation time, ascending).

### create_note
- [ ] `create_note(document_id: int, *, note: str) -> DocumentNote` sends `POST /documents/{document_id}/notes/` with `{"note": "<text>"}` and returns the newly created `DocumentNote`.
- [ ] The `note` parameter is required and must be a non-empty string (enforced by the server).
- [ ] Returns the newly created note object (not the full list).
- [ ] Raises `NotFoundError` when the document does not exist (HTTP 404).

### delete_note
- [ ] `delete_note(document_id: int, note_id: int) -> None` sends `DELETE /documents/{document_id}/notes/?id={note_id}` and returns `None` on success.
- [ ] Raises `NotFoundError` when the document or note does not exist (HTTP 404).

### DocumentNote model
- [ ] `DocumentNote` exposes: `id`, `note`, `created`, `document`, `user`.
- [ ] `id` is the unique note ID (integer).
- [ ] `note` is the text content.
- [ ] `created` is the creation timestamp (`datetime`).
- [ ] `document` is the parent document ID (integer).
- [ ] `user` is the ID of the user who created the note (integer, may be `None`).

### General
- [ ] No `update_note` method is provided — the paperless-ngx API has no PATCH/PUT endpoint for notes.
- [ ] All methods are available on `SyncPaperlessClient` with identical signatures (blocking wrapper).

## Edge Cases
- `create_note` with an empty string `note` → server returns HTTP 400; error propagated as-is.
- `delete_note` with a `note_id` that belongs to a different document → server returns HTTP 404; raised as `NotFoundError`.
- `get_notes` on a document with many notes → all notes returned in a single response (paperless-ngx does not paginate notes).
- Concurrent deletion of the same note → second call raises `NotFoundError`; callers should handle this gracefully.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
