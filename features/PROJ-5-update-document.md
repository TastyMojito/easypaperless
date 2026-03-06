# PROJ-5: Update Document

## Status: Partially Implemented
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
_To be added by /qa_

## Deployment
_To be added by /deploy_
