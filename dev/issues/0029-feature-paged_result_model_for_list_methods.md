# [FEATURE] Return PagedResult Model from All list() Methods

## Summary

All resource `list()` methods currently return a plain `list[T]`, discarding the pagination metadata that the paperless-ngx API includes in every list response (`count`, `next`, `previous`, and optionally `all`). This feature introduces a generic `PagedResult[T]` model and changes every `list()` method to return it, giving callers access to the total item count and raw page links.

---

## Problem Statement

The API response for any list endpoint has the form:

```json
{
  "count": 123,
  "next": "http://example.org/api/documents/?page=4",
  "previous": "http://example.org/api/documents/?page=2",
  "all": [4, 2, 1],
  "results": [...]
}
```

Currently, easypaperless strips this envelope and returns only `results` as a plain Python list. Callers lose:

- `count` — the total number of matching items (useful for progress reporting, UI display, deciding whether to paginate).
- `next` / `previous` — raw page URLs (useful when callers want to drive pagination themselves).
- `all` — the list of all matching IDs (when provided by the API).

This forces callers to either over-fetch or implement their own counting logic.

---

## Proposed Solution

Introduce a generic `PagedResult[T]` Pydantic model in the public `easypaperless` namespace. Change every `list()` method across all resources — for both the async and sync clients — to return `PagedResult[T]` instead of `list[T]`.

The model holds:

| Field | Type | Description |
|---|---|---|
| `count` | `int` | Total number of matching items as reported by the server on the first fetched page. |
| `next` | `str \| None` | URL of the next page as returned by the API. |
| `previous` | `str \| None` | URL of the previous page as returned by the API. |
| `all` | `list[int] \| None` | All matching IDs when the API includes them; `None` otherwise. |
| `results` | `list[T]` | The actual resource items. |

### Auto-pagination behaviour

When `page` is `None` (the default), easypaperless automatically fetches all pages and collects every item into `results`. In this mode, `next` and `previous` are always set to `None` in the returned model — even if `max_results` truncates the final result set — because the navigation URLs are meaningless once pagination has been fully consumed by the library. This behaviour must be clearly documented on every affected method.

When `page` is set to a specific integer, easypaperless fetches exactly that one page and returns the `next` / `previous` values from the API response verbatim.

---

## User Stories

- As a developer, I want to know the total count of matching documents without fetching every page so that I can display progress or decide whether to paginate further.
- As a developer, I want access to `next` and `previous` page URLs when requesting a single page so that I can implement my own pagination loop.
- As a developer, I want the full list of matching IDs when available so that I can use them for bulk operations without iterating all results.

---

## Scope

### In Scope

- New generic `PagedResult[T]` Pydantic model exported from the top-level `easypaperless` namespace.
- Return type change for `list()` on: `DocumentsResource`, `TagsResource`, `CorrespondentsResource`, `DocumentTypesResource`, `StoragePathsResource`, `CustomFieldsResource` — both async and sync variants.
- Clear documentation (docstrings) on each `list()` method explaining that `next`/`previous` are `None` during auto-pagination.
- Minor version bump (breaking change).

### Out of Scope

- Adding new pagination control parameters (these already exist: `page`, `page_size`, `max_results`).
- Changing the behaviour of any non-list method.
- Exposing raw HTTP response headers.
- Backwards-compatibility shim for the old `list[T]` return type.

---

## Acceptance Criteria

- [ ] A `PagedResult[T]` generic Pydantic model exists and is exported from `easypaperless.__init__`.
- [ ] `PagedResult` has fields: `count: int`, `next: str | None`, `previous: str | None`, `all: list[int] | None`, `results: list[T]`.
- [ ] Every `list()` method on every resource (async and sync) returns `PagedResult[T]` where `T` is the appropriate item model.
- [ ] When auto-pagination is active (default, `page=None`): `next` and `previous` in the returned `PagedResult` are `None`; `count` reflects the total from the server's first page response; `results` contains all fetched items.
- [ ] When `max_results` truncates the result: `next` and `previous` are still `None`; `count` still reflects the server total (not the truncated length).
- [ ] When a single page is requested (`page=<int>`): `next` and `previous` contain the raw URL strings from the API response (or `None` if absent).
- [ ] `all` is `None` when the API response does not include the `all` field.
- [ ] All existing `list()` parameters (filters, ordering, pagination controls, callbacks) continue to work unchanged.
- [ ] Mypy (strict) passes with no new errors.
- [ ] Ruff lint and format checks pass.
- [ ] All existing tests are updated to match the new return type.
- [ ] New unit tests cover: auto-pagination result shape, single-page result shape, `max_results` truncation result shape, `all` field present vs absent.
- [ ] Docstrings on each `list()` method document the `next`/`previous`=`None` behaviour for auto-pagination.

---

## Dependencies & Constraints

- Affects issue #0003 (Document List with Filters) implementation — all acceptance criteria for that issue remain valid except the return type.
- This is a breaking change to the public API; a minor version bump is required.

---

## Priority

`High`

---

## Additional Notes

The `all` field is only present in some API responses (observed in certain resource list endpoints). The model must tolerate its absence gracefully.
