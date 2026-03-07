# PROJ-10: Tags CRUD

## Status: QA Passed
**Created:** 2026-03-06
**Last Updated:** 2026-03-07

## Dependencies
- Requires: PROJ-1 (HTTP Client Core) — for authenticated HTTP requests and error mapping

## User Stories
- As a developer, I want to list all tags so that I can inspect what tags exist in my paperless-ngx instance.
- As a developer, I want to filter tags by name substring so that I can find a tag without loading the full list.
- As a developer, I want to fetch a single tag by ID so that I can read its properties.
- As a developer, I want to create a new tag with name, colour, inbox flag, auto-match settings, and parent so that I can manage the tag taxonomy programmatically.
- As a developer, I want to update an existing tag so that I can rename it, change its colour, or adjust its auto-match rules.
- As a developer, I want to delete a tag so that I can remove unused tags without using the web UI.
- As a developer, I want to assign an owner and explicit permissions when creating a tag so that access control is set up at creation time.

## Acceptance Criteria

### list_tags
- [ ] `list_tags(*, ids, name_contains, page, page_size, ordering, descending) -> list[Tag]` fetches `GET /tags/` and returns validated `Tag` instances.
- [ ] `ids` filters to only tags whose ID is in the list (`id__in` query param).
- [ ] `name_contains` does a case-insensitive substring match on tag name (`name__icontains`).
- [ ] When `page` is omitted, all pages are fetched automatically (auto-pagination).
- [ ] When `page` is set, only that page is returned (disables auto-pagination).
- [ ] `ordering` + `descending` control sort order; `descending=True` prepends `-` to the field name.

### get_tag
- [ ] `get_tag(id: int) -> Tag` fetches `GET /tags/{id}/` and returns a validated `Tag`.
- [ ] Raises `NotFoundError` on HTTP 404.

### create_tag
- [ ] `create_tag(*, name, color, is_inbox_tag, match, matching_algorithm, is_insensitive, parent, owner, set_permissions) -> Tag` sends `POST /tags/` and returns the created `Tag`.
- [ ] `name` is required; all other fields are optional.
- [ ] `color` is a CSS hex string (e.g. `"#ff0000"`).
- [ ] `is_inbox_tag=True` marks the tag as the inbox tag; newly ingested documents receive it automatically.
- [ ] `matching_algorithm` integer values: `0`=none, `1`=any word, `2`=all words, `3`=exact, `4`=regex, `5`=fuzzy, `6`=auto (ML).
- [ ] `parent` accepts a tag ID to place the new tag in a hierarchy; `None` creates a root-level tag.
- [ ] `owner` sets the owning user ID; `None` leaves the tag without an owner.
- [ ] `set_permissions` sets explicit view/change permissions via `SetPermissions` model.

### update_tag
- [ ] `update_tag(id: int, *, name, color, is_inbox_tag, match, matching_algorithm, is_insensitive, parent) -> Tag` sends `PATCH /tags/{id}/` and returns the updated `Tag`.
- [ ] Only fields explicitly passed (not `None`) are included in the payload.
- [ ] Raises `NotFoundError` on HTTP 404.
- [ ] `owner` and `set_permissions` are **not yet supported** in `update_tag` (planned — consistent with the same gap in `update_document`).

### delete_tag
- [ ] `delete_tag(id: int) -> None` sends `DELETE /tags/{id}/` and returns `None` on success.
- [ ] Raises `NotFoundError` on HTTP 404.

### General
- [ ] The `Tag` model exposes: `id`, `name`, `slug`, `color`, `text_color`, `match`, `matching_algorithm`, `is_insensitive`, `is_inbox_tag`, `document_count`, `owner`, `user_can_change`, `parent`, `children`.
- [ ] All methods are available on `SyncPaperlessClient` with the same signatures (blocking wrapper).

## Edge Cases
- Creating a tag with a name that already exists → server returns an error (likely HTTP 400); propagated as-is.
- Deleting a tag that is assigned to documents — paperless-ngx removes the tag from those documents; no error is raised.
- `is_inbox_tag=True` when another tag is already the inbox tag — paperless-ngx allows multiple inbox tags; behaviour is server-defined.
- `parent` pointing to a non-existent tag ID → server returns an error; propagated as-is.
- `update_tag` called with no keyword arguments → empty PATCH payload; server returns the tag unchanged.

---
<!-- Sections below are added by subsequent skills -->

## Tech Design (Solution Architect)
_To be added by /architecture_

## QA Test Results
**Tested:** 2026-03-07
**Tester:** QA Engineer (automated)
**Verdict:** PRODUCTION-READY

### Acceptance Criteria Results

#### list_tags
| # | Criterion | Result |
|---|-----------|--------|
| 1 | `list_tags(*, ids, name_contains, page, page_size, ordering, descending) -> list[Tag]` fetches `GET /tags/` and returns validated `Tag` instances | PASS |
| 2 | `ids` filters to only tags whose ID is in the list (`id__in` query param) | PASS |
| 3 | `name_contains` does a case-insensitive substring match on tag name (`name__icontains`) | PASS |
| 4 | When `page` is omitted, all pages are fetched automatically (auto-pagination) | PASS |
| 5 | When `page` is set, only that page is returned (disables auto-pagination) | PASS |
| 6 | `ordering` + `descending` control sort order; `descending=True` prepends `-` to the field name | PASS |

#### get_tag
| # | Criterion | Result |
|---|-----------|--------|
| 7 | `get_tag(id: int) -> Tag` fetches `GET /tags/{id}/` and returns a validated `Tag` | PASS |
| 8 | Raises `NotFoundError` on HTTP 404 | PASS |

#### create_tag
| # | Criterion | Result |
|---|-----------|--------|
| 9 | `create_tag(*, name, color, is_inbox_tag, match, matching_algorithm, is_insensitive, parent, owner, set_permissions) -> Tag` sends `POST /tags/` and returns the created `Tag` | PASS |
| 10 | `name` is required; all other fields are optional | PASS |
| 11 | `color` is a CSS hex string (e.g. `"#ff0000"`) | PASS |
| 12 | `is_inbox_tag=True` marks the tag as the inbox tag | PASS |
| 13 | `matching_algorithm` integer values: 0-6 via `MatchingAlgorithm` IntEnum | PASS |
| 14 | `parent` accepts a tag ID; `None` creates a root-level tag | PASS |
| 15 | `owner` sets the owning user ID; `None` leaves the tag without an owner | PASS |
| 16 | `set_permissions` sets explicit view/change permissions via `SetPermissions` model | PASS |

#### update_tag
| # | Criterion | Result |
|---|-----------|--------|
| 17 | `update_tag(id, *, name, color, is_inbox_tag, match, matching_algorithm, is_insensitive, parent) -> Tag` sends `PATCH /tags/{id}/` and returns the updated `Tag` | PASS |
| 18 | Only fields explicitly passed (not `None`) are included in the payload | PASS |
| 19 | Raises `NotFoundError` on HTTP 404 | PASS |
| 20 | `owner` and `set_permissions` are not supported in `update_tag` (by design) | PASS |

#### delete_tag
| # | Criterion | Result |
|---|-----------|--------|
| 21 | `delete_tag(id: int) -> None` sends `DELETE /tags/{id}/` and returns `None` on success | PASS |
| 22 | Raises `NotFoundError` on HTTP 404 | PASS |

#### General
| # | Criterion | Result |
|---|-----------|--------|
| 23 | `Tag` model exposes: `id`, `name`, `slug`, `color`, `text_color`, `match`, `matching_algorithm`, `is_insensitive`, `is_inbox_tag`, `document_count`, `owner`, `user_can_change`, `parent`, `children` | PASS |
| 24 | All methods available on `SyncPaperlessClient` with same signatures | PASS |

**Total: 24/24 PASSED**

### Edge Cases Tested
| Edge Case | Result |
|-----------|--------|
| `update_tag` called with no keyword arguments (empty PATCH payload) | PASS — server returns tag unchanged |
| Cache invalidation after create/update/delete | PASS — resolver cache invalidated on all mutating operations |

### Code Quality
| Check | Result |
|-------|--------|
| `pytest tests/test_client_tags.py` (100 tests) | PASS — all 100 passed |
| `pytest tests/` (full suite, 353 tests) | PASS — all 353 passed |
| Test coverage (tags modules) | 100% — 0 lines missed |
| `ruff check` (linting) | PASS — no issues |
| `mypy` (type checking) | PASS — no issues |
| `ruff format --check` | OBSERVATION — see below |

### Observations
| # | Severity | Description |
|---|----------|-------------|
| 1 | Low | `ruff format --check` reports formatting differences in `_internal/mixins/tags.py` and `_internal/sync_mixins/tags.py` (parenthesization of `cast()` calls and `self._run()` calls). This is a **project-wide** pattern affecting 15 mixin files across PROJ-10 through PROJ-14, not specific to tags. Cosmetic only; does not affect functionality. |

### Regression Testing
- Full test suite (353 tests) passes with no regressions.
- `SyncPaperlessClient` tags tests (5 sync tag tests in `test_sync.py`) all pass.
- Related features (PROJ-1 HTTP core, PROJ-2 resolver, PROJ-9 bulk ops) unaffected.

### Production-Ready: YES
No Critical or High severity bugs. All 24 acceptance criteria pass. 100% test coverage. The single low-severity formatting observation is cosmetic and project-wide.

## Deployment
_To be added by /deploy_
