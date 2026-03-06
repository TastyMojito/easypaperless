# PROJ-13: Custom Fields CRUD

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to list all custom fields so that I can discover what structured metadata is defined in my paperless-ngx instance.
- As a developer, I want to fetch a single custom field by ID so that I can read its name, data type, and configuration.
- As a developer, I want to create a new custom field with a specific data type so that I can add structured metadata to documents.
- As a developer, I want to create a select-type custom field with predefined options so that document values are constrained to a known list.
- As a developer, I want to rename a custom field or update its select options so that I can maintain the field schema over time.
- As a developer, I want to delete a custom field so that I can remove unused structured metadata.

## Acceptance Criteria

### list_custom_fields
- [ ] `list_custom_fields(*, page, page_size, ordering, descending) -> list[CustomField]` fetches `GET /custom_fields/` and returns validated `CustomField` instances.
- [ ] When `page` is omitted, all pages are fetched automatically (auto-pagination).
- [ ] When `page` is set, only that page is returned (disables auto-pagination).
- [ ] `ordering` + `descending` control sort order; `descending=True` prepends `-` to the field name.
- [ ] `ids` and `name_contains` filters are **not supported** for this resource (the paperless-ngx API does not expose these query params for custom fields).

### get_custom_field
- [ ] `get_custom_field(id: int) -> CustomField` fetches `GET /custom_fields/{id}/` and returns a validated `CustomField`.
- [ ] Raises `NotFoundError` on HTTP 404.

### create_custom_field
- [ ] `create_custom_field(*, name, data_type, extra_data, owner, set_permissions) -> CustomField` sends `POST /custom_fields/` and returns the created `CustomField`.
- [ ] `name` and `data_type` are required; all other fields are optional.
- [ ] `data_type` must be one of: `"string"`, `"boolean"`, `"integer"`, `"float"`, `"monetary"`, `"date"`, `"url"`, `"documentlink"`, `"select"`. These are represented by the `FieldDataType` enum.
- [ ] For `data_type="select"`, `extra_data` configures allowed values via a `select_options` key. The API *returns* options as objects `{"id": "<generated-string>", "label": "<display-text>"}`. The accepted *create* format (plain strings vs. full objects) is **not confirmed — needs verification against a live instance**. Current code docstring documents plain strings: `{"select_options": ["Option A", "Option B"]}`.
- [ ] For all other data types, `extra_data` should be `None`.
- [ ] `owner` sets the owning user ID; `None` leaves the field without an owner.
- [ ] `set_permissions` sets explicit view/change permissions via `SetPermissions` model.

### update_custom_field
- [ ] `update_custom_field(id: int, *, name, extra_data) -> CustomField` sends `PATCH /custom_fields/{id}/` and returns the updated `CustomField`.
- [ ] Only fields explicitly passed (not `None`) are included in the payload.
- [ ] `data_type` is intentionally **not** a parameter — the paperless-ngx API does not allow changing the data type of an existing field. To change the type, the field must be deleted and recreated.
- [ ] Passing `extra_data=None` is a no-op and does not clear the existing `extra_data` value.
- [ ] Raises `NotFoundError` on HTTP 404.

### delete_custom_field
- [ ] `delete_custom_field(id: int) -> None` sends `DELETE /custom_fields/{id}/` and returns `None` on success.
- [ ] Raises `NotFoundError` on HTTP 404.

### General
- [ ] The `CustomField` model exposes: `id`, `name`, `data_type` (as `FieldDataType` enum), `extra_data`, `document_count`.
- [ ] The `FieldDataType` enum is exported as part of the public API.
- [ ] All methods are available on `SyncPaperlessClient` with the same signatures (blocking wrapper).

## Edge Cases
- Creating a custom field with a name that already exists → server returns an error (likely HTTP 400); propagated as-is.
- Creating a `"select"` field without supplying valid `extra_data` (i.e. without `select_options`) → server may return an error; client does not validate this.
- Deleting a custom field that has values on existing documents — paperless-ngx removes those `CustomFieldValue` entries from all documents; no error is raised.
- Attempting to change `data_type` via `update_custom_field` is not possible; the parameter is simply absent from the method — callers cannot accidentally send it.
- `update_custom_field` called with no keyword arguments → empty PATCH payload; server returns the custom field unchanged.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
