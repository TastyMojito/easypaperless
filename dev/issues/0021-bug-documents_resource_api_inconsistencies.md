# [BUG] Documents Resource API Inconsistencies

## Summary

Four API inconsistencies exist in `DocumentsResource` that make the interface confusing or incorrect: a wrong parameter name in `update()`, an inconsistent abbreviation for archive serial number across methods, a wrong default value in `search_mode`, and a missing type in `upload()`.

---

## Bugs

### 1. `update()`: parameter `date` should be named `created`

`DocumentsResource.update()` exposes the creation date field as `date`, but the paperless-ngx API field is `created`, and `upload()` already uses `created` for the same concept. This inconsistency forces users to learn two names for the same field.

**Actual:** `documents.update(id, date="2024-01-01")`
**Expected:** `documents.update(id, created="2024-01-01")`

---

### 2. `update()` and `upload()`: `asn` should be named `archive_serial_number`

`DocumentsResource.update()` and `upload()` expose the archive serial number field as `asn`. However, `DocumentsResource.list()` already uses the full name `archive_serial_number` for the same concept. The abbreviation is inconsistent with the rest of the API surface.

**Actual:** `documents.update(id, asn=42)` / `documents.upload(..., asn=42)`
**Expected:** `documents.update(id, archive_serial_number=42)` / `documents.upload(..., archive_serial_number=42)`

---

### 3. `list()`: `search_mode` default and map key `"title_or_text"` should be `"title_or_content"`

`DocumentsResource.list()` uses `"title_or_text"` as the name for the combined title/content search mode. The paperless-ngx field is called `content`, not `text`. The internal `_SEARCH_MODE_MAP` key and the default value of `search_mode` must both be updated to `"title_or_content"` for consistency with the field name.

**Actual:** `search_mode="title_or_text"` (default), map key `"title_or_text"`
**Expected:** `search_mode="title_or_content"` (default), map key `"title_or_content"`

---

### 4. `upload()`: `created` parameter accepts only `str`, should also accept `date`

`DocumentsResource.upload()` declares `created: str | None = None`. Other date parameters throughout the resource accept `date | str`. The `created` parameter in `upload()` should accept a Python `date` object in addition to an ISO-8601 string, consistent with the rest of the API.

**Actual:** `created: str | None = None`
**Expected:** `created: date | str | None = None`

---

## Impact

- **Severity:** `Medium`
- **Affected:** All callers of `DocumentsResource.update()`, `upload()`, and `list()`.

---

## Acceptance Criteria

- [ ] `DocumentsResource.update()` parameter `date` is renamed to `created`. The payload key sent to the API remains `"created"`.
- [ ] `DocumentsResource.update()` parameter `asn` is renamed to `archive_serial_number`. The payload key sent to the API remains `"archive_serial_number"`.
- [ ] `DocumentsResource.upload()` parameter `asn` is renamed to `archive_serial_number`. The multipart field sent to the API remains `"archive_serial_number"`.
- [ ] `_SEARCH_MODE_MAP` key `"title_or_text"` is renamed to `"title_or_content"`. The mapped API value (`"search"`) remains unchanged.
- [ ] `DocumentsResource.list()` default for `search_mode` is updated from `"title_or_text"` to `"title_or_content"`.
- [ ] `DocumentsResource.upload()` `created` parameter type is widened to `date | str | None`. A `date` value is formatted to an ISO-8601 string before being sent to the API.
- [ ] All sync counterparts (`SyncDocumentsResource`) are updated in lockstep.
- [ ] Docstrings are updated to reflect the new parameter names and types.
- [ ] Ruff linting and Mypy type checking pass without errors.
- [ ] Existing tests are updated to use the new parameter names; all tests pass.

---

## Additional Notes

- These are breaking renames — callers using keyword arguments will need to update. Because the package has not yet reached a stable 1.x release, this is acceptable without a major version bump, but the changes must be documented in the CHANGELOG.
- No changes to model fields or API query keys are required; only Python parameter names and types change.
