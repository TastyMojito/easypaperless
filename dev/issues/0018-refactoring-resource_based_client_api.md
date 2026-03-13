# [REFACTORING] Resource-Based Client API

## Summary

The client currently exposes a flat method namespace (e.g. `client.list_documents()`, `client.create_tag()`). This refactoring replaces that with a resource-based namespace (e.g. `client.documents.list()`, `client.tags.create()`) for both `PaperlessClient` and `SyncPaperlessClient`. The old flat methods are removed entirely.

---

## Current State

All resource operations are exposed as top-level methods on the client, e.g.:

- `client.list_documents()`
- `client.get_document(id)`
- `client.update_document(id, ...)`
- `client.delete_document(id)`
- `client.download_document(id)`
- `client.upload_document(...)`
- `client.list_tags()`, `client.create_tag()`, `client.delete_tag()`, ...
- `client.list_correspondents()`, `client.list_document_types()`, etc.
- `client.list_custom_fields()`, `client.list_storage_paths()`, etc.
- `client.get_notes(doc_id)`, `client.create_note(...)`, etc.
- Document bulk operations as flat methods on the client root:
  - Low-level: `client.bulk_edit()`
  - High-level helpers: `client.bulk_add_tag()`, `client.bulk_remove_tag()`, `client.bulk_modify_tags()`, `client.bulk_delete()`, `client.bulk_set_correspondent()`, `client.bulk_set_document_type()`, `client.bulk_set_storage_path()`, `client.bulk_modify_custom_fields()`, `client.bulk_set_permissions()`
- Non-document bulk operations as flat methods on the client root:
  - Low-level: `client.bulk_edit_objects()`
  - High-level helpers: `client.bulk_delete_tags()`, `client.bulk_set_permissions_tags()`, `client.bulk_delete_correspondents()`, `client.bulk_set_permissions_correspondents()`, `client.bulk_delete_document_types()`, `client.bulk_set_permissions_document_types()`, `client.bulk_delete_storage_paths()`, `client.bulk_set_permissions_storage_paths()`

This flat structure makes method discovery harder as the number of resources grows and does not reflect the natural grouping of operations by resource.

---

## Desired State

Resource operations are accessed via sub-namespaces on the client:

- `client.documents.list()`, `.get(id)`, `.update(id, ...)`, `.delete(id)`, `.download(id)`, `.upload(...)`
- Document bulk operations on `client.documents`:
  - Low-level: `client.documents.bulk_edit()`
  - High-level helpers: `client.documents.bulk_add_tag()`, `client.documents.bulk_remove_tag()`, `client.documents.bulk_modify_tags()`, `client.documents.bulk_delete()`, `client.documents.bulk_set_correspondent()`, `client.documents.bulk_set_document_type()`, `client.documents.bulk_set_storage_path()`, `client.documents.bulk_modify_custom_fields()`, `client.documents.bulk_set_permissions()`
- `client.documents.notes.list(doc_id)`, `.create(...)`, `.delete(...)`
- `client.tags.list()`, `.get(id)`, `.create(...)`, `.update(id, ...)`, `.delete(id)`
  - Bulk: `client.tags.bulk_delete()`, `client.tags.bulk_set_permissions()`
- `client.correspondents.list()`, `.get(id)`, `.create(...)`, `.update(id, ...)`, `.delete(id)`
  - Bulk: `client.correspondents.bulk_delete()`, `client.correspondents.bulk_set_permissions()`
- `client.document_types.list()`, `.get(id)`, `.create(...)`, `.update(id, ...)`, `.delete(id)`
  - Bulk: `client.document_types.bulk_delete()`, `client.document_types.bulk_set_permissions()`
- `client.custom_fields.list()`, `.get(id)`, `.create(...)`, `.update(id, ...)`, `.delete(id)`
- `client.storage_paths.list()`, `.get(id)`, `.create(...)`, `.update(id, ...)`, `.delete(id)`
  - Bulk: `client.storage_paths.bulk_delete()`, `client.storage_paths.bulk_set_permissions()`

The flat top-level methods are removed. The public interface exported from `__init__.py` remains `PaperlessClient` and `SyncPaperlessClient`.

---

## Motivation

- [x] Improve maintainability
- [x] Improve readability
- [x] Align with current standards / conventions

---

## Scope

### In Scope

- Restructure `PaperlessClient` to expose resource sub-objects for all resource groups: `documents`, `tags`, `correspondents`, `document_types`, `custom_fields`, `storage_paths`
- Document notes accessible as `client.documents.notes`
- Restructure `SyncPaperlessClient` identically
- Remove all flat top-level resource methods from both clients
- Update all existing tests to use the new API
- Update public documentation (README, docstrings, examples) to reflect the new API

### Out of Scope

- Backward-compatible shims or deprecation warnings for old flat methods
- Changes to the underlying HTTP layer, models, or mixins beyond what is needed for restructuring
- Adding new resource operations not already implemented

---

## Risks & Considerations

- This is a **breaking change** to the public API. Any user code using the flat method API will break. This is acceptable because the package wasn't publicly announced yet and is only used by the developer himself.
- The CHANGELOG must clearly document the breaking change and the migration path.
- All existing tests reference flat methods and must be updated as part of this issue.

---

## Acceptance Criteria

- [ ] Existing behavior is fully preserved (no functional changes) — all operations that existed before still exist, only accessible via the new namespace.
- [ ] `client.documents.list()`, `.get()`, `.update()`, `.delete()`, `.download()`, `.upload()` all work correctly.
- [ ] `client.documents.bulk_edit()` (low-level) and all high-level document bulk helpers (`bulk_add_tag`, `bulk_remove_tag`, `bulk_modify_tags`, `bulk_delete`, `bulk_set_correspondent`, `bulk_set_document_type`, `bulk_set_storage_path`, `bulk_modify_custom_fields`, `bulk_set_permissions`) are accessible on `client.documents` and work correctly.
- [ ] `client.documents.notes.list()`, `.create()`, `.delete()` all work correctly.
- [ ] `client.tags`, `client.correspondents`, `client.document_types`, `client.storage_paths` each expose `.list()`, `.get()`, `.create()`, `.update()`, `.delete()`, `.bulk_delete()`, and `.bulk_set_permissions()`.
- [ ] `client.custom_fields` exposes `.list()`, `.get()`, `.create()`, `.update()`, `.delete()` (no bulk operations).
- [ ] No flat resource methods remain on the top-level client (verified by inspection of public API).
- [ ] Both `PaperlessClient` (async) and `SyncPaperlessClient` (sync) follow the same resource-based structure.
- [ ] All tests pass without modification to test logic (only API call paths updated).
- [ ] README quickstart examples are updated to the new API.
- [ ] CHANGELOG entry documents the breaking change and migration.

---

## Priority

`Medium`

---

## Additional Notes

- Related to all existing resource issues (PROJ-3 through PROJ-17) which defined the original flat-method API.
- Versioning: this change warrants a major version bump (semver).
