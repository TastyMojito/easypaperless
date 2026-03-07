"""Custom fields resource mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from easypaperless.models.custom_fields import CustomField
from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession
    from easypaperless._internal.resolvers import NameResolver


class CustomFieldsMixin:
    if TYPE_CHECKING:
        _session: HttpSession
        _resolver: NameResolver

        async def _list_resource(
            self, resource: str, model_class: type[Any], params: dict[str, Any] | None = None
        ) -> list[Any]: ...

        async def _get_resource(
            self, resource: str, id: int, model_class: type[Any]
        ) -> Any: ...

        async def _create_resource(
            self,
            resource: str,
            model_class: type[Any],
            *,
            owner: int | None = None,
            set_permissions: SetPermissions | None = None,
            **kwargs: Any,
        ) -> Any: ...

        async def _update_resource(
            self, resource: str, id: int, model_class: type[Any], **kwargs: Any
        ) -> Any: ...

        async def _delete_resource(self, resource: str, id: int) -> None: ...

    async def list_custom_fields(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[CustomField]:
        """Return all custom fields defined in paperless-ngx.

        Args:
            page: Return only this specific page (1-based). Disables
                auto-pagination. Default: ``None`` (return all).
            page_size: Number of results per page. When omitted, the server
                default is used.
            ordering: Field to sort by. Examples: ``"name"``, ``"id"``.
            descending: When ``True``, reverses the sort direction of
                ``ordering``. Ignored when ``ordering`` is ``None``.

        Returns:
            List of
            :class:`~easypaperless.models.custom_fields.CustomField`
            objects.
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if ordering is not None:
            params["ordering"] = f"-{ordering}" if descending else ordering
        return cast(
            list[CustomField],
            await self._list_resource("custom_fields", CustomField, params or None),
        )

    async def get_custom_field(self, id: int) -> CustomField:
        """Fetch a single custom field by its ID.

        Args:
            id: Numeric custom-field ID.

        Returns:
            The :class:`~easypaperless.models.custom_fields.CustomField`
            with the given ID.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no custom field
                exists with that ID.
        """
        return cast(CustomField, await self._get_resource("custom_fields", id, CustomField))

    async def create_custom_field(
        self,
        *,
        name: str,
        data_type: str,
        extra_data: Any | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> CustomField:
        """Create a new custom field.

        Args:
            name: Field name shown in the UI. Must be unique.
            data_type: Value type. One of ``"string"``, ``"boolean"``,
                ``"integer"``, ``"float"``, ``"monetary"``, ``"date"``,
                ``"url"``, ``"documentlink"``, ``"select"``.
            extra_data: Additional configuration for the field type. For
                ``data_type="select"``, pass
                ``{"select_options": ["Option A", "Option B"]}``. For all
                other types, leave as ``None``.
            owner: Numeric user ID to assign as owner. ``None`` creates the
                field with no owner (visible to all users).
            set_permissions: Explicit view/change permission sets. Defaults to
                no permissions (all users have access via public visibility).

        Returns:
            The newly created
            :class:`~easypaperless.models.custom_fields.CustomField`.
        """
        return cast(CustomField, await self._create_resource(
            "custom_fields",
            CustomField,
            owner=owner,
            set_permissions=set_permissions,
            name=name,
            data_type=data_type,
            extra_data=extra_data,
        ))

    async def update_custom_field(
        self,
        id: int,
        *,
        name: str | None = None,
        extra_data: Any | None = None,
    ) -> CustomField:
        """Partially update a custom field (PATCH semantics).

        Note:
            ``data_type`` is intentionally excluded — the paperless-ngx API
            does not allow changing the type of an existing custom field. To
            change the type, delete and recreate the field.

        Args:
            id: Numeric ID of the custom field to update.
            name: Field name shown in the UI. Must be unique.
            extra_data: Additional configuration for the field type (e.g.
                ``{"select_options": ["Option A", "Option B"]}`` for select
                fields). Passing ``None`` is a no-op and will not clear the
                existing value.

        Returns:
            The updated
            :class:`~easypaperless.models.custom_fields.CustomField`.
        """
        return cast(CustomField, await self._update_resource(
            "custom_fields",
            id,
            CustomField,
            name=name,
            extra_data=extra_data,
        ))

    async def delete_custom_field(self, id: int) -> None:
        """Delete a custom field.

        Args:
            id: Numeric ID of the custom field to delete.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no custom field
                exists with that ID.
        """
        await self._delete_resource("custom_fields", id)
