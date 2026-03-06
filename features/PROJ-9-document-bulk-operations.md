# PROJ-9: Document Bulk Operations

## Status: Partially Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping
- Requires: PROJ-2 (Name-to-ID Resolver) — for transparent string-to-ID resolution of tag, correspondent, document type, and storage path names

## User Stories
- As a developer, I want to add a tag to many documents in a single request so that I don't have to loop over individual `update_document` calls.
- As a developer, I want to remove a tag from many documents in a single request so that I can efficiently untag a batch.
- As a developer, I want to atomically add and remove multiple tags on a set of documents in one request so that the batch update is consistent and requires only one round trip.
- As a developer, I want to permanently delete many documents in a single request so that bulk cleanup is fast.
- As a developer, I want to assign a correspondent, document type, or storage path to many documents at once so that I can re-organise a batch without looping.
- As a developer, I want to add and/or remove custom field values on many documents at once so that I can update structured metadata in bulk.
- As a developer, I want to set permissions and owner on many documents at once so that I can apply access control to an entire batch.
- As a developer, I want a low-level escape hatch to call any bulk-edit method the paperless-ngx API supports, so that operations not yet covered by high-level helpers are still accessible.

## Acceptance Criteria

### High-level helpers
- [ ] `bulk_add_tag(document_ids: list[int], tag: int | str) -> None` adds a single tag to all listed documents. `tag` accepts an ID or name.
- [ ] `bulk_remove_tag(document_ids: list[int], tag: int | str) -> None` removes a single tag from all listed documents. `tag` accepts an ID or name.
- [ ] `bulk_modify_tags(document_ids: list[int], *, add_tags: list[int | str] | None, remove_tags: list[int | str] | None) -> None` atomically adds and/or removes multiple tags on all listed documents. Both parameters accept IDs or names and are optional (passing neither is a no-op).
- [ ] `bulk_delete(document_ids: list[int]) -> None` permanently deletes all listed documents.
- [ ] All high-level helpers accept string tag names and resolve them to IDs transparently before sending the request.
- [ ] All methods return `None` on success.

### Metadata assignment helpers (planned)
- [ ] `bulk_set_correspondent(document_ids: list[int], correspondent: int | str | None) -> None` assigns a correspondent to all listed documents. Accepts an ID or name; `None` clears the assignment.
- [ ] `bulk_set_document_type(document_ids: list[int], document_type: int | str | None) -> None` assigns a document type to all listed documents. Accepts an ID or name; `None` clears the assignment.
- [ ] `bulk_set_storage_path(document_ids: list[int], storage_path: int | str | None) -> None` assigns a storage path to all listed documents. Accepts an ID or name; `None` clears the assignment.
- [ ] `bulk_modify_custom_fields(document_ids: list[int], *, add_fields: list[dict] | None, remove_fields: list[int] | None) -> None` atomically adds and/or removes custom field values on all listed documents.
- [ ] `bulk_set_permissions(document_ids: list[int], *, set_permissions: SetPermissions | None, owner: int | None, merge: bool = False) -> None` applies permissions and/or owner to all listed documents. When `merge=True`, the new permissions are merged with existing ones rather than replacing them.
- [ ] `bulk_set_correspondent`, `bulk_set_document_type`, and `bulk_set_storage_path` accept string names and resolve them to IDs transparently.

### Low-level primitive
- [ ] `bulk_edit(document_ids: list[int], method: str, **parameters) -> None` sends `POST /documents/bulk_edit/` with payload `{"documents": document_ids, "method": method, "parameters": parameters}`.
- [ ] `bulk_edit` uses an extended request timeout of 120 seconds (large batches can take considerably longer than the default).
- [ ] All high-level helpers are implemented on top of `bulk_edit`.

### General
- [ ] All methods are available on `SyncPaperlessClient` with the same signatures (blocking wrapper).

## Edge Cases
- Empty `document_ids` list — the request is sent as-is; the API treats it as a no-op.
- `bulk_modify_tags` called with both `add_tags=None` and `remove_tags=None` — resolves to empty lists and sends `modify_tags` with empty arrays (no-op on the server).
- A tag name passed to any helper does not exist in paperless-ngx → resolver raises an error before the HTTP request is made.
- Large batches may approach the 120-second timeout; the extended timeout is applied per-request. If the server still times out, the underlying HTTP error propagates to the caller.
- `bulk_delete` is permanent and irreversible — no confirmation or undo mechanism is provided by this API.
- `bulk_edit` is a low-level method; passing an unknown `method` string will be forwarded to the API which may return an error — the caller is responsible for using valid method names.

## Out of Scope
- Bulk operations on non-document resources (tags, correspondents, etc.) — covered by a separate feature (`bulk_edit_objects`).

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
