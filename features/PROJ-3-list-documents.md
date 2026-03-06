# PROJ-3: Document List with Filters

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for HTTP session and pagination
- Requires: PROJ-2 (Name-to-ID Resolver) — for transparent name-to-ID resolution on FK filters

## User Stories
- As a developer, I want to call `list_documents()` with no arguments and get all documents so that I can iterate the full archive without writing pagination logic.
- As a developer, I want to fetch a specific set of documents by their IDs in a single call so that I can efficiently retrieve a known list without filtering by other attributes.
- As a developer, I want to filter documents by tags, correspondents, document types, and storage paths using either integer IDs or human-readable names so that I don't have to look up IDs manually.
- As a developer, I want to filter documents by owner so that I can scope results to documents belonging to a specific user.
- As a developer, I want to search documents by title substring, full-text, query language, or original filename so that I can use the most appropriate search mode for my use case.
- As a developer, I want to filter by date ranges (created, added, modified) so that I can scope results to a specific time window.
- As a developer, I want to control pagination (page size, specific page, max results) so that I can manage memory usage and latency for large libraries.
- As a developer, I want a progress callback (`on_page`) so that I can display a progress indicator when fetching large result sets.
- As a developer, I want to sort results by any field in ascending or descending order so that I can consume documents in a predictable sequence.
- As a developer, I want to filter documents by whether specific custom fields are set so that I can find documents that have (or are missing) particular metadata.
- As a developer, I want to filter documents by custom field values (equality, range, substring, etc.) using a structured query so that I can leverage all custom field types without constructing raw API query strings.

## Acceptance Criteria

### Method Signature
- [ ] `PaperlessClient.list_documents(...)` is an `async` method returning `list[Document]`.
- [ ] All parameters are keyword-only.

### Search
- [ ] `search` + `search_mode="title_or_text"` (default) maps to API `search` param (Whoosh FTS).
- [ ] `search_mode="title"` maps to API `title__icontains`.
- [ ] `search_mode="query"` maps to API `query` (paperless query language).
- [ ] `search_mode="original_filename"` maps to API `original_filename__icontains`.
- [ ] When `search` is `None`, no search parameter is sent to the API.

### ID Filter
- [ ] `ids: list[int] | None` — return only documents whose ID is in this list; maps to `id__in`.

### Tag Filters
- [ ] `tags: list[int | str] | None` — documents must have **all** listed tags (AND semantics → `tags__id__all`).
- [ ] `any_tag: list[int | str] | None` — documents must have **at least one** listed tag (OR semantics → `tags__id__in`).
- [ ] `exclude_tags: list[int | str] | None` — documents must have **none** of the listed tags (`tags__id__none`).
- [ ] All tag parameters accept tag IDs (int) or tag names (str); names are resolved transparently via PROJ-2.

### Correspondent Filters
- [ ] `correspondent: int | str | None` — exact match; resolved to ID then sent as `correspondent__id__in`.
- [ ] `any_correspondent: list[int | str] | None` — OR semantics; takes precedence over `correspondent` when both are provided.
- [ ] `exclude_correspondents: list[int | str] | None` — exclusion filter (`correspondent__id__none`).
- [ ] All correspondent parameters accept IDs or names.

### Document Type Filters
- [ ] `document_type: int | str | None` — exact match; sent as API `document_type`.
- [ ] `any_document_type: list[int | str] | None` — OR semantics (`document_type__id__in`); takes precedence over `document_type` when both are provided.
- [ ] `exclude_document_types: list[int | str] | None` — exclusion filter (`document_type__id__none`).
- [ ] All document-type parameters accept IDs or names.

### Storage Path Filters
- [ ] `storage_path: int | str | None` — filter to documents assigned to exactly this storage path. Accepts a storage path ID or name.
- [ ] `any_storage_paths: list[int | str] | None` — OR semantics (`storage_path__id__in`); takes precedence over `storage_path` when both are provided.
- [ ] `exclude_storage_paths: list[int | str] | None` — exclusion filter (`storage_path__id__none`).
- [ ] All storage path parameters accept IDs or names; names are resolved transparently via PROJ-2.

### Owner Filters
- [ ] `owner: int | None` — filter to documents owned by this user ID; maps to `owner__id__in`.
- [ ] `exclude_owners: list[int] | None` — exclude documents owned by any of these user IDs; maps to `owner__id__none`.
- [ ] Owner parameters accept integer user IDs only (users are not a named resource in PROJ-2).

### Date Filters
- [ ] `created_after: date | str | None` — ISO-8601 `"YYYY-MM-DD"`; maps to `created__date__gt`.
- [ ] `created_after: date | str | None` — ISO-8601 `"YYYY-MM-DD"`; maps to `created__date__gt`.
- [ ] `created_before: date | str | None` — ISO-8601 `"YYYY-MM-DD"`; maps to `created__date__lt`.
- [ ] `created_before: date | str | None` — ISO-8601 `"YYYY-MM-DD"`; maps to `created__date__lt`.
- [ ] `added_after: date | datetime | str | None` — maps to `added__date__gt`, if value is a date and maps to `added__gt` if value is a datetime.
- [ ] `added_from: date | datetime | str | None` — maps to `added__date__gte`, if value is a date and maps to `added__gte` if value is a datetime.
- [ ] `added_before: date | datetime | str | None` — maps to `added__date__lt`, if value is a date and maps to `added__lt` if value is a datetime.
- [ ] `added_until: date | datetime | str | None` — maps to `added__date__lte`, if value is a date and maps to `added__lte` if value is a datetime.
- [ ] `modified_after: date | datetime | str | None` — maps to `modified__date__gt`, if value is a date and maps to `modified__gt` if value is a datetime.
- [ ] `modified_from: date | datetime | str | None` — maps to `modified__date__gte`, if value is a date and maps to `modified__gte` if value is a datetime.
- [ ] `modified_before: date | datetime | str | None` — maps to `modified__date__lt`, if value is a date and maps to `modified__lt` if value is a datetime.
- [ ] `modified_until: date | datetime | str | None` — maps to `modified__date__lte`, if value is a date and maps to `modified__lte` if value is a datetime.

### Custom Field Existence Filters
These filters check whether a custom field is set on the document, without regard to the field's value.

- [ ] `custom_fields: list[int | str] | None` — documents must have **all** listed custom fields set (not null, AND semantics → `custom_fields__id__all`). Accepts custom field IDs or names.
- [ ] `any_custom_fields: list[int | str] | None` — documents must have **at least one** listed custom field set (OR semantics → `custom_fields__id__in`). Accepts IDs or names.
- [ ] `exclude_custom_fields: list[int | str] | None` — documents must have **none** of the listed custom fields set (`custom_fields__id__none`). Accepts IDs or names.
- [ ] All existence filter params resolve custom field names to IDs transparently via PROJ-2.

### Custom Field Value Filter
- [ ] `custom_field_query: list | None` — filter documents by custom field values using a structured query. Accepts a native Python list which is serialized to the API's JSON query format. Default: `None`.
- [ ] Simple form: `[field_name_or_id, operator, value]` — e.g. `["Invoice Amount", "gt", 100]`.
- [ ] Compound form: `["AND" | "OR", [[cond1], [cond2], ...]]` and `["NOT", [cond]]`.
- [ ] Field references accept either an integer custom field ID or a string custom field name.
- [ ] Supported operators by data type:

  | Data type | Supported operators |
  |-----------|-------------------|
  | All types | `exact`, `in`, `isnull`, `exists` |
  | `string`, `url`, `longtext` | + `icontains`, `istartswith`, `iendswith` |
  | `integer`, `float`, `monetary` | + `gt`, `gte`, `lt`, `lte`, `range` |
  | `date` | + `gt`, `gte`, `lt`, `lte`, `range` |
  | `select` | `exact`, `in` |
  | `documentlink` | `contains` (accepts document IDs) |

- [ ] The API enforces a maximum nesting depth of 10 and a maximum of 20 atomic conditions per query; violations raise an error from the server.

### Other Filters
- [ ] `archive_serial_number: int | None` — filter by archive serial number; maps to `archive_serial_number`.
- [ ] `archive_serial_number_from: int | None` — filter by archive serial number; maps to `archive_serial_number__gte`.
- [ ] `archive_serial_number_till: int | None` — filter by archive serial number; maps to `archive_serial_number__lte`.
- [ ] `checksum: str | None` — MD5 checksum exact match; maps to `checksum`.

### Pagination
- [ ] `page_size: int` — number of results per API page; default `25`.
- [ ] `page: int | None` — when set, fetches only that single page (1-based) and disables auto-pagination; default `None`.
- [ ] When `page` is `None`, the method auto-paginates through all pages until `next` is `null` in the API response.
- [ ] `max_results: int | None` — stop after collecting this many documents; default `None` (no limit). Applies only during auto-pagination.
- [ ] `on_page: Callable[[int, int | None], None] | None` — callback invoked after each page fetch; receives `(fetched_so_far, total)` where `total` is the server-reported count from the first page (may be `None`). Ignored when `page` is set.

### Ordering
- [ ] `ordering: str | None` — field name to sort by (e.g., `"created"`, `"title"`, `"added"`); default `None` (server default).
- [ ] `descending: bool` — when `True`, prepends `-` to the ordering field name; default `False`. Ignored when `ordering` is `None`.

### Return Value
- [ ] Each item in the returned list is a validated `Document` Pydantic model.
- [ ] When the result comes from an FTS search, each `Document` has its `search_hit` field populated from the `__search_hit__` key in the API response.

## Edge Cases
- **No results:** Returns an empty list `[]` without error.
- **Single-page result:** Auto-pagination terminates correctly after the first (and only) page.
- **`any_correspondent` + `correspondent` both provided:** `any_correspondent` takes precedence; `correspondent` is silently ignored.
- **`any_document_type` + `document_type` both provided:** `any_document_type` takes precedence; `document_type` is silently ignored.
- **`any_storage_paths` + `storage_path` both provided:** `any_storage_paths` takes precedence; `storage_path` is silently ignored.
- **`max_results` smaller than `page_size`:** The method still fetches a full first page but returns only `max_results` documents.
- **Name resolution failure:** Raises `NotFoundError` (from PROJ-2) when a tag/correspondent/document-type/storage-path name cannot be resolved.
- **Unknown `search_mode`:** Falls back to API `search` param (same as `"title_or_text"`).
- **`page` set with `on_page` provided:** `on_page` callback is ignored (no pagination occurs).
- **`custom_field_query` exceeds API limits:** The server returns an error if nesting depth > 10 or atom count > 20; this is surfaced as a `ServerError` to the caller.
- **Custom field name not found in `custom_fields` / `any_custom_fields` / `exclude_custom_fields`:** Raises `NotFoundError` via PROJ-2.
- **Custom field name used inside `custom_field_query`:** Names are passed through as-is to the API (no resolution); the API resolves them server-side. Invalid names result in a server error.

## Technical Requirements
- No breaking changes to the `Document` model for fields not returned by the list endpoint (e.g., `metadata` remains `None`).
- Name resolution calls are batched per-resource using PROJ-2's `resolve_list`; a single `list_documents` call must not issue more resolution requests than there are distinct FK parameters.
- The `any_tag` parameter name is a known inconsistency with the api-conventions (which prefer `any_tags`). It is preserved for backwards compatibility in this release.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
