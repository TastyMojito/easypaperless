# [BUG] `is_insensitive` Default Misleads Users in `create()` Methods

## Summary

The `is_insensitive` parameter in `correspondents.create()`, `document_types.create()`, `storage_paths.create()`, and `tags.create()` defaults to `None`, causing it to be omitted from the API request. The paperless-ngx API defaults this field to `True`, so the actual behaviour when `is_insensitive` is not specified is case-insensitive matching — but the Python signature suggests `None` (no value / off), which is misleading. The default should be `True` to make the actual behaviour explicit and discoverable.

---

## Steps to Reproduce

1. Call `correspondents.create(name="ACME")` without passing `is_insensitive`.
2. Observe that the created correspondent has case-insensitive matching enabled (API default `True`).
3. Read the method signature: `is_insensitive: bool | None = None` — suggests the value will be absent/`None`, not `True`.

---

## Expected Behavior

The Python default `True` makes the actual API behaviour visible in the signature. Callers who do not supply `is_insensitive` get the same result as the API default, and tools like IDEs and `help()` show the real default.

---

## Actual Behavior

The Python default `None` causes the field to be omitted from the request body. The API silently applies its own default (`True`), so users who read the signature get a false impression that no value is set, while the API actually enables case-insensitive matching.

---

## Impact

- **Severity:** `Low`
- **Affected:** All callers of `correspondents.create()`, `document_types.create()`, `storage_paths.create()`, and `tags.create()` who rely on the default behaviour without reading the API documentation.

---

## Scope

### In Scope

- Change the default of `is_insensitive` from `None` to `True` in:
  - `CorrespondentsResource.create()`
  - `DocumentTypesResource.create()`
  - `StoragePathsResource.create()`
  - `TagsResource.create()`
- Update docstrings to state the default is `True`.
- Update all sync counterparts in lockstep.

### Out of Scope

- `update()` methods — there `None` correctly means "leave unchanged" (UNSET semantics via the sentinel pattern). No change needed.
- Any other parameters or resources.
- Verifying the API default for other boolean fields.

---

## Acceptance Criteria

- [ ] `CorrespondentsResource.create()` declares `is_insensitive: bool = True`.
- [ ] `DocumentTypesResource.create()` declares `is_insensitive: bool = True`.
- [ ] `StoragePathsResource.create()` declares `is_insensitive: bool = True`.
- [ ] `TagsResource.create()` declares `is_insensitive: bool = True`.
- [ ] When `is_insensitive=True` is the default, the value is always included in the API request body (not omitted when it equals the default).
- [ ] All sync resource counterparts expose the same default.
- [ ] Docstrings for each affected method state that the default is `True`.
- [ ] Ruff linting and Mypy type checking pass without errors.
- [ ] Existing tests continue to pass; new or updated tests verify the default value is sent in the request body.

---

## Additional Notes

- Before implementing, confirm that the paperless-ngx API default for `is_insensitive` is indeed `True` against a live instance or the official API docs, in case the assumption is wrong.
- This is a breaking change for any caller who explicitly relied on omitting the field to get the API default, but in practice the behaviour is identical — only the Python signature changes.
