# [TASK] Complete Missing Parameters Across Resource Methods

## Summary

Several resource methods are missing parameters that are supported by the paperless-ngx API. This task tracks adding all identified missing parameters to bring the wrapper into full parity with the API.

---

## Background / Context

A review of the current resource implementations against the paperless-ngx API revealed a number of parameters that are accepted by the API but not exposed in the wrapper's method signatures. Without these parameters, users cannot access the full functionality of the API through easypaperless.

---

## Objectives

- Add all missing parameters to the affected resource methods so that each method fully covers the corresponding API endpoint's available parameters.

---

## Scope

### In Scope

- `CorrespondentsResource.update()`: add `owner`, `set_permissions`
- `CustomFieldsResource.list()`: add `name_contains`, `name_exact`
- `CustomFieldsResource.update()`: add `data_type`
- `DocumentTypesResource.update()`: add `owner`, `set_permissions`
- `DocumentsResource.list()`: add `document_type_name_exact`, `document_type_name_contains`
- `DocumentsResource.update()`: add `remove_inbox_tags`
- `DocumentsResource.upload()`: add `custom_fields`
- `StoragePathsResource.list()`: add `path_exact`, `path_contains`
- `StoragePathsResource.update()`: add `owner`, `set_permissions`
- `TagsResource.update()`: add `owner`, `set_permissions`
- All sync counterparts (`SyncCorrespondentsResource`, `SyncCustomFieldsResource`, etc.) must be updated in lockstep.

### Out of Scope

- Adding new methods (e.g., new endpoints not yet covered)
- Changing existing parameter names or types
- Changes to models not directly required by the new parameters
- Documentation beyond docstring updates for the affected methods

---

## Acceptance Criteria

- [ ] `CorrespondentsResource.update()` accepts `owner` and `set_permissions` parameters and passes them to the API.
- [ ] `CustomFieldsResource.list()` accepts `name_contains` and `name_exact` filter parameters and passes them to the API.
- [ ] `CustomFieldsResource.update()` accepts `data_type` parameter and passes it to the API.
- [ ] `DocumentTypesResource.update()` accepts `owner` and `set_permissions` parameters and passes them to the API.
- [ ] `DocumentsResource.list()` accepts `document_type_name_exact` and `document_type_name_contains` filter parameters and passes them to the API.
- [ ] `DocumentsResource.update()` accepts `remove_inbox_tags` parameter and passes it to the API.
- [ ] `DocumentsResource.upload()` accepts `custom_fields` parameter and passes it to the API.
- [ ] `StoragePathsResource.list()` accepts `path_exact` and `path_contains` filter parameters and passes them to the API.
- [ ] `StoragePathsResource.update()` accepts `owner` and `set_permissions` parameters and passes them to the API.
- [ ] `TagsResource.update()` accepts `owner` and `set_permissions` parameters and passes them to the API.
- [ ] All sync resource counterparts expose the same parameters as their async equivalents.
- [ ] All new parameters use the `UNSET` sentinel (not `None`) as default to distinguish "omitted" from explicit null, consistent with the existing pattern.
- [ ] Ruff linting and Mypy type checking pass without errors.
- [ ] Existing tests continue to pass.

---

## Dependencies

- Issue #0019 (UNSET sentinel) — must be merged first, as new parameters should follow that pattern. (Already implemented.)

---

## Priority

`Medium`

---

## Additional Notes

- `owner` and `set_permissions` appear in multiple resources; verify the exact payload format the API expects for each (may differ between resource types).
- `set_permissions` for storage paths was identified via the UI, not the public API docs — confirm it is accepted by the API before implementing.
- Parameter names listed above are based on user observation and may differ from the actual API field names — verify the exact names against the paperless-ngx API documentation or a live instance before implementing.
