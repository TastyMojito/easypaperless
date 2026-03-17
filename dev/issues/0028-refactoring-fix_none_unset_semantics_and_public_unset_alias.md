# [REFACTORING] Fix None/Unset Semantics Across Async Resource Methods and Expose Public `Unset` Alias

> ⚠️ **Mid-implementation change (2026-03-17):** The originally specified semantics for `set_permissions` have been revised during implementation. The previous spec said `set_permissions` cannot be `None` and should default to `UNSET`. The new spec intentionally allows `None` as a meaningful value — see updated Desired State below.

## Summary

A manual audit of all async resource method signatures revealed two classes of problems:
(1) several parameters accept `None` where `None` has no meaningful semantic (only `UNSET` makes sense as the "not provided" default), and
(2) the `_Unset` sentinel type is private, so pdoc renders it as `easypaperless._internal.sentinel._Unset` in signatures instead of a short readable public name.

This refactoring corrects both issues consistently across all async resource classes. The sync mirrors must be updated in the same pass.

---

## Current State

### Parameter semantic errors

The following parameters currently default to or accept `None` but should only ever be `UNSET` as the "not provided" sentinel. Passing `None` to them has no meaningful effect on the API call or is actively misleading:

**Correspondents**
- `create()`: `match`, `matching_algorithm` — `None` currently means "use paperless default", should be `UNSET`
- `update()`: `name`, `match`, `matching_algorithm`, `is_insensitive` — cannot be `None`
- `bulk_set_permissions()`: `owner` — can be `None` (clear owner), but default must be `UNSET`

**Custom Fields**
- `update()`: `name`, `data_type` — cannot be `None`
- `update()`: missing `owner` and `set_permissions` parameters entirely

**Document Types**
- Same pattern as Correspondents for `create()`, `update()`, `bulk_set_permissions()`

**Documents**
- `update()`: `title`, `content` — cannot be `None`
- `upload()`: `title` — cannot be `None`, default `UNSET`
- `bulk_set_permissions()`: `owner` — can be `None` (clear), default must be `UNSET`

**Storage Paths**
- `create()`: `path`, `match`, `matching_algorithm` — cannot be `None`
- `update()`: `name`, `path`, `match`, `matching_algorithm`, `is_insensitive` — cannot be `None`
- `bulk_set_permissions()`: `owner` — can be `None` (clear), default must be `UNSET`

**Tags**
- `create()`: `color`, `is_inbox_tag` — cannot be `None`, default `UNSET`; `match`, `matching_algorithm` — cannot be `None`, default `UNSET`
- `update()`: `name`, `color`, `is_inbox_tag`, `match`, `matching_algorithm`, `is_insensitive` — cannot be `None`
- `bulk_set_permissions()`: `owner` — can be `None` (clear), default must be `UNSET`

### Legacy `Optional[]` style

Several `list()` methods and `upload()` use `Optional[X]` instead of `X | None`. These should be updated to the modern union syntax for consistency.

### Private `_Unset` type in pdoc output

The sentinel type `_Unset` is defined in `easypaperless._internal.sentinel` and is not exported from the public package. pdoc therefore renders parameter signatures as `param: int | None | easypaperless._internal.sentinel._Unset = UNSET`, which is confusing for end-users reading the generated documentation.

---

## Desired State

### Consistent None / Unset semantics

The following rules must be applied uniformly:

| Context | Semantic | Default |
|---|---|---|
| `create()` — optional param where paperless applies its own default | "not provided by caller" | `UNSET` |
| `create()` / `update()` — nullable param (e.g. `owner`) | `None` = set to null, `UNSET` = not provided | `UNSET` |
| `update()` — required-if-present field (e.g. `name`, `title`) | cannot be `None` at all; type is `str`, not `str | None` | `UNSET` |
| `update()` — non-nullable param (e.g. `match`, `matching_algorithm`, `is_insensitive`) | cannot be `None`; type reflects only valid values | `UNSET` |
| `list()` — filter param where `None` means "filter not set" | `None` = do not apply filter | `None` |
| `list()` — filter param where `None` means "filter for null" | `None` = active filter for null; `UNSET` = filter not set | `UNSET` |

All `Optional[X]` usages should be replaced with `X | None`.

### `set_permissions` semantics (revised 2026-03-17)

`set_permissions` is a special parameter that requires three-way semantics in both `create()` and `update()` methods. The type in all resource method signatures must be `SetPermissions | None | Unset`.

| Value | Meaning in `create()` | Meaning in `update()` |
|---|---|---|
| `UNSET` (default) | Omit `set_permissions` from the request payload entirely; let paperless-ngx apply its own default | Do not touch permissions; leave them unchanged |
| `None` | Send an empty `SetPermissions` object (i.e. `SetPermissions().model_dump()`); explicitly create without any permissions | Overwrite existing permissions with an empty `SetPermissions` object; i.e. clear all permissions |
| `SetPermissions(...)` | Send the provided permissions | Overwrite existing permissions with the provided value |

**Responsibility boundary:**

- All resource `create()` and `update()` methods accept `set_permissions: SetPermissions | None | Unset = UNSET` and pass the value through to `_ClientCore._create_resource()` or `_ClientCore._update_resource()` without any conversion or branching logic.
- `_ClientCore._create_resource()` and `_ClientCore._update_resource()` in `client.py` are responsible for translating the three-way value into the correct JSON payload entry. No `set_permissions`-related conversion logic belongs in individual resource files.

### Public `Unset` alias

A public type alias `Unset` is added to the package public API (e.g. exported from `easypaperless/__init__.py` or a dedicated `easypaperless/types.py`). The internal `_Unset` class is aliased as `Unset`. All async and sync resource method signatures that currently reference `_Unset` must use `Unset` instead, so that pdoc renders e.g.:

```
owner: int | None | Unset = UNSET
```

The `UNSET` sentinel constant is also re-exported publicly alongside `Unset`.

### Sync mirrors updated

All sync resource methods in `_internal/sync_resources/` must be updated to reflect the same signature corrections applied to their async counterparts.

---

## Motivation
- [x] Improve readability
- [x] Align with current standards / conventions
- [x] Reduce complexity (centralise `set_permissions` handling in `_ClientCore`; remove scattered conversion logic from resource files)

---

## Scope

### In Scope
- All async resource classes in `_internal/resources/`: `correspondents.py`, `custom_fields.py`, `document_types.py`, `documents.py`, `storage_paths.py`, `tags.py`
- All sync resource classes in `_internal/sync_resources/` (same files)
- `_ClientCore._create_resource()` and `_ClientCore._update_resource()` in `client.py`
- Expose `Unset` and `UNSET` from the public package API
- Replace `Optional[X]` with `X | None` throughout all resource method signatures
- Add missing `owner` and `set_permissions` parameters to `CustomFieldsResource.update()`
- Remove dead code that handles `None` for parameters where `None` is not a valid value (e.g. `if match is None: ...` inside `create()` for `match`)

### Out of Scope
- Changes to Pydantic models in `models/`
- Changes to `_internal/http.py` or `_internal/resolvers.py`
- Changing the behavior of `list()` filter parameters that already correctly use `None` as "filter not set"
- Any changes to the `UNSET` sentinel implementation itself
- `bulk_set_permissions()` methods — these have their own payload-building logic and are not affected by the `_create_resource` / `_update_resource` change

---

## Risks & Considerations

- Removing `None`-handling code for parameters like `match` and `matching_algorithm` in `create()` is a behavior change for callers who currently pass `None` explicitly expecting it to mean "use default". This is acceptable because that usage is semantically incorrect and was never the intended contract.
- Adding `owner` and `set_permissions` to `CustomFieldsResource.update()` is a net-new capability, not a regression.
- Exposing `Unset` publicly is additive and non-breaking.
- The sync mirrors must be updated in the same pass to avoid divergence.
- The revised `set_permissions = None` semantics (clear permissions) is a deliberate, intentional behavior addition. Callers who previously omitted `set_permissions` are unaffected; callers who previously passed `None` explicitly (which was previously rejected by the type system) now get a well-defined clearing behavior.

---

## Acceptance Criteria
- [ ] Existing behavior is fully preserved for all parameters where `None` remains a valid value (nullable fields like `owner`).
- [ ] All parameters where `None` was incorrect now use `UNSET` as default; their type annotations exclude `None`.
- [ ] Dead `None`-handling code for non-nullable parameters is removed from `create()` and `update()` implementations.
- [ ] `Optional[X]` is replaced with `X | None` throughout all resource method signatures in both async and sync resources.
- [ ] `Unset` (the type) and `UNSET` (the sentinel value) are exported from `easypaperless.__init__` (or a public `easypaperless.types` module re-exported from `__init__`).
- [ ] pdoc-generated documentation renders parameter types as e.g. `owner: int | None | Unset = UNSET`. (ask the user about this, don't check yourself!)
- [ ] `CustomFieldsResource.update()` includes `owner` and `set_permissions` parameters.
- [ ] All resource `create()` methods accept `set_permissions: SetPermissions | None | Unset = UNSET` and pass it through to `_create_resource()` without any local conversion.
- [ ] All resource `update()` methods accept `set_permissions: SetPermissions | None | Unset = UNSET` and pass it through to `_update_resource()` without any local conversion.
- [ ] `_ClientCore._create_resource()`: when `set_permissions` is `UNSET`, the key is omitted from the payload; when `None`, `SetPermissions().model_dump()` is sent; when a `SetPermissions` instance, `set_permissions.model_dump()` is sent.
- [ ] `_ClientCore._update_resource()`: same three-way behavior as `_create_resource()`.
- [ ] All existing tests pass without modification.
- [ ] `mypy --strict` passes with no new errors.
- [ ] `ruff check` and `ruff format --check` pass.

---

## Priority
`High`

---

## Additional Notes
- Related: #0019 (original None/UNSET bug that introduced the sentinel), #0020 (missing params), #0021 (documents inconsistencies), #0022 (is_insensitive default)
- The public `Unset` alias pattern follows the convention used by e.g. `httpx` and `anthropic` SDK, where internal sentinels are exposed under clean public names.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-17
**Commit:** 4c0e8eb

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: Nullable fields (`owner`) preserve `None` as valid value | `None` included in payload | `None` included in payload | ✅ Pass |
| 2 | AC: Non-nullable params default to `UNSET`; type excludes `None` | `color`, `match`, etc. are `X \| Unset` not `X \| None` | Types correct across all resources | ✅ Pass |
| 3 | AC: Dead `None`-handling code removed from `create()` / `update()` | No `if x is None` guards for non-nullable params | No such guards found in any resource file | ✅ Pass |
| 4 | AC: `Optional[X]` replaced with `X \| None` throughout | No `Optional[...]` in resource signatures | Grep confirms zero occurrences | ✅ Pass |
| 5 | AC: `Unset` and `UNSET` exported from `easypaperless.__init__` and `__all__` | Both in `__all__`; importable from top-level | Confirmed in `__init__.py`; tests pass | ✅ Pass |
| 6 | AC: pdoc renders `Unset` (not `_internal.sentinel._Unset`) | Ask user — not checked automatically | Not tested (per AC instruction) | ⬜ Untested |
| 7 | AC: `CustomFieldsResource.update()` includes `owner` and `set_permissions` | Both params present with correct types | Present with `int \| None \| Unset` and `SetPermissions \| None \| Unset` | ✅ Pass |
| 8 | AC: All `create()` methods accept `set_permissions: SetPermissions \| None \| Unset = UNSET` and pass through | Param present, no local conversion | Verified for all 5 resource classes (tags, correspondents, doc_types, storage_paths, custom_fields) | ✅ Pass |
| 9 | AC: All `update()` methods accept `set_permissions: SetPermissions \| None \| Unset = UNSET` and pass through | Param present, no local conversion | Verified for all 5 resource classes | ✅ Pass |
| 10 | AC: `_create_resource()` — `UNSET` omits key, `None` sends empty `SetPermissions`, value sends `.model_dump()` | Three-way behavior | Confirmed in `client.py`; 4 tests pass | ✅ Pass |
| 11 | AC: `_update_resource()` — same three-way behavior | Same as above | Confirmed in `client.py`; 4 tests pass | ✅ Pass |
| 12 | AC: All existing tests pass without modification | 538 tests pass | 538 passed | ✅ Pass |
| 13 | AC: `mypy --strict` passes with no new errors | No type errors | `Success: no issues found in 32 source files` | ✅ Pass |
| 14 | AC: `ruff check` and `ruff format --check` pass | No lint/format errors | 1 ruff I001 error in test file | ❌ Fail |
| 20 | BUG-001 fix: `ruff check` and `ruff format --check` pass on fixed test file | No ruff errors | Both pass with no errors | ✅ Pass |
| 15 | Edge: `set_permissions=None` + `owner=None` sent together | Both appear in payload | Both sent correctly | ✅ Pass |
| 16 | Edge: Non-nullable params absent from payload when omitted | Not in body | Confirmed for all resources | ✅ Pass |
| 17 | Edge: Non-nullable params present when explicitly provided | In body with correct value | Confirmed | ✅ Pass |
| 18 | Sync mirrors: `set_permissions` pass-through works correctly | Same three-way behavior | 4 sync tests pass | ✅ Pass |
| 19 | Sentinel: `_Unset = Unset` alias kept in `sentinel.py` | `_Unset` is `Unset` | Confirmed; no other `_Unset` usage in source | ✅ Pass |

### Bugs Found

#### BUG-001 — Ruff I001 import order violation in test file [Severity: Low] ✅ Fixed
**Steps to reproduce:**
1. Run `ruff check .` in the project root.

**Expected:** No ruff errors.
**Actual:** `tests/test_issue_0028_none_unset_semantics.py:99` — `I001 Import block is un-sorted or un-formatted` — the local import `from easypaperless import UNSET as PublicUNSET, Unset as PublicUnset` has the two names in the wrong alphabetical order (should be `Unset as PublicUnset, UNSET as PublicUNSET` or sorted by original name).
**Severity:** Low (test-file only; no runtime impact; auto-fixable with `ruff --fix`)
**Notes:** `ruff format --check` also exits non-zero because of this single violation.
**Fix:** Split into two separate `from easypaperless import ...` statements. `ruff check` and `ruff format --check` now pass on this file.

### Automated Tests
- Suite: `pytest tests/` (excl. integration) — **538 passed**, 0 failed
- Suite: `pytest tests/test_issue_0028_none_unset_semantics.py` — **38 passed**, 0 failed
- `mypy src/easypaperless/` — **Success**, no issues in 32 source files

### Summary
- ACs tested: 14/15 (1 untested — pdoc rendering, per spec instruction to ask user)
- ACs passing: 14/14 tested (after BUG-001 fix)
- ACs failing: 0
- Bugs found: 1 (Critical: 0, High: 0, Medium: 0, Low: 1) — all fixed
- Recommendation: ✅ Ready to merge
