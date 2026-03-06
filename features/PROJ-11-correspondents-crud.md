# PROJ-11: Correspondents CRUD

## Status: Implemented
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to list all correspondents so that I can inspect who is tracked in my paperless-ngx instance.
- As a developer, I want to filter correspondents by name substring so that I can find one without loading the full list.
- As a developer, I want to fetch a single correspondent by ID so that I can read its properties.
- As a developer, I want to create a new correspondent with name, auto-match settings, and permissions so that I can manage correspondents programmatically.
- As a developer, I want to update an existing correspondent so that I can rename it or adjust its auto-match rules.
- As a developer, I want to delete a correspondent so that I can remove unused ones without using the web UI.

## Acceptance Criteria

### list_correspondents
- [ ] `list_correspondents(*, ids, name_contains, page, page_size, ordering, descending) -> list[Correspondent]` fetches `GET /correspondents/` and returns validated `Correspondent` instances.
- [ ] `ids` filters to only correspondents whose ID is in the list (`id__in` query param).
- [ ] `name_contains` does a case-insensitive substring match on correspondent name (`name__icontains`).
- [ ] When `page` is omitted, all pages are fetched automatically (auto-pagination).
- [ ] When `page` is set, only that page is returned (disables auto-pagination).
- [ ] `ordering` + `descending` control sort order; `descending=True` prepends `-` to the field name.

### get_correspondent
- [ ] `get_correspondent(id: int) -> Correspondent` fetches `GET /correspondents/{id}/` and returns a validated `Correspondent`.
- [ ] Raises `NotFoundError` on HTTP 404.

### create_correspondent
- [ ] `create_correspondent(*, name, match, matching_algorithm, is_insensitive, owner, set_permissions) -> Correspondent` sends `POST /correspondents/` and returns the created `Correspondent`.
- [ ] `name` is required; all other fields are optional.
- [ ] `matching_algorithm` integer values: `0`=none, `1`=any word, `2`=all words, `3`=exact, `4`=regex, `5`=fuzzy, `6`=auto (ML).
- [ ] `owner` sets the owning user ID; `None` leaves the correspondent without an owner.
- [ ] `set_permissions` sets explicit view/change permissions via `SetPermissions` model.

### update_correspondent
- [ ] `update_correspondent(id: int, *, name, match, matching_algorithm, is_insensitive) -> Correspondent` sends `PATCH /correspondents/{id}/` and returns the updated `Correspondent`.
- [ ] Only fields explicitly passed (not `None`) are included in the payload.
- [ ] Raises `NotFoundError` on HTTP 404.
- [ ] `owner` and `set_permissions` are **not yet supported** in `update_correspondent` (planned — consistent with the same gap in `update_document` and `update_tag`).

### delete_correspondent
- [ ] `delete_correspondent(id: int) -> None` sends `DELETE /correspondents/{id}/` and returns `None` on success.
- [ ] Raises `NotFoundError` on HTTP 404.

### General
- [ ] The `Correspondent` model exposes: `id`, `name`, `slug`, `match`, `matching_algorithm`, `is_insensitive`, `document_count`, `last_correspondence`, `owner`, `user_can_change`.
- [ ] All methods are available on `SyncPaperlessClient` with the same signatures (blocking wrapper).

## Edge Cases
- Creating a correspondent with a name that already exists → server returns an error (likely HTTP 400); propagated as-is.
- Deleting a correspondent that is assigned to documents — paperless-ngx clears the correspondent field on those documents; no error is raised.
- `update_correspondent` called with no keyword arguments → empty PATCH payload; server returns the correspondent unchanged.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
_To be added by /qa_

## Deployment
_To be added by /deploy_
