"""Storage paths resource mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.permissions import SetPermissions
from easypaperless.models.storage_paths import StoragePath

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession
    from easypaperless._internal.resolvers import NameResolver


class StoragePathsMixin:
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

    async def list_storage_paths(
        self,
        *,
        ids: list[int] | None = None,
        name_contains: str | None = None,
        name_exact: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[StoragePath]:
        """Return storage paths defined in paperless-ngx.

        Args:
            ids: Return only storage paths whose ID is in this list.
            name_contains: Case-insensitive substring filter on storage-path
                name (raw API ``name__icontains``).
            name_exact: Case-insensitive exact match on storage-path name
                (raw API ``name__iexact``).
            page: Return only this specific page (1-based). Disables
                auto-pagination. Default: ``None`` (return all).
            page_size: Number of results per page. When omitted, the server
                default is used.
            ordering: Field to sort by. Examples: ``"name"``, ``"id"``.
            descending: When ``True``, reverses the sort direction of
                ``ordering``. Ignored when ``ordering`` is ``None``.

        Returns:
            List of
            :class:`~easypaperless.models.storage_paths.StoragePath`
            objects.
        """
        params: dict[str, Any] = {}
        if ids is not None:
            params["id__in"] = ",".join(str(i) for i in ids)
        if name_contains is not None:
            params["name__icontains"] = name_contains
        if name_exact is not None:
            params["name__iexact"] = name_exact
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if ordering is not None:
            params["ordering"] = f"-{ordering}" if descending else ordering
        return cast(
            list[StoragePath],
            await self._list_resource("storage_paths", StoragePath, params or None),
        )

    async def get_storage_path(self, id: int) -> StoragePath:
        """Fetch a single storage path by its ID.

        Args:
            id: Numeric storage-path ID.

        Returns:
            The :class:`~easypaperless.models.storage_paths.StoragePath`
            with the given ID.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no storage path
                exists with that ID.
        """
        return cast(StoragePath, await self._get_resource("storage_paths", id, StoragePath))

    async def create_storage_path(
        self,
        *,
        name: str,
        path: str | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> StoragePath:
        """Create a new storage path.

        Args:
            name: Storage-path name. Must be unique.
            path: Template string for the archive file path. Supported
                placeholders: ``{created_year}``, ``{created_month}``,
                ``{created_day}``, ``{correspondent}``, ``{document_type}``,
                ``{title}``, ``{asn}``. Example:
                ``"{created_year}/{correspondent}/{title}"``. When omitted,
                the server default location is used.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.
            owner: Numeric user ID to assign as owner. ``None`` creates the
                storage path with no owner (visible to all users).
            set_permissions: Explicit view/change permission sets. Defaults to
                no permissions (all users have access via public visibility).

        Returns:
            The newly created
            :class:`~easypaperless.models.storage_paths.StoragePath`.
        """
        return cast(StoragePath, await self._create_resource(
            "storage_paths",
            StoragePath,
            owner=owner,
            set_permissions=set_permissions,
            name=name,
            path=path,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    async def update_storage_path(
        self,
        id: int,
        *,
        name: str | None = None,
        path: str | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
    ) -> StoragePath:
        """Partially update a storage path (PATCH semantics).

        Args:
            id: Numeric ID of the storage path to update.
            name: Storage-path name. Must be unique.
            path: Template string for the archive file path. Supported
                placeholders: ``{created_year}``, ``{created_month}``,
                ``{created_day}``, ``{correspondent}``, ``{document_type}``,
                ``{title}``, ``{asn}``. Example: ``"{title}"``.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.

        Returns:
            The updated
            :class:`~easypaperless.models.storage_paths.StoragePath`.
        """
        return cast(StoragePath, await self._update_resource(
            "storage_paths",
            id,
            StoragePath,
            name=name,
            path=path,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    async def delete_storage_path(self, id: int) -> None:
        """Delete a storage path.

        Args:
            id: Numeric ID of the storage path to delete.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no storage path
                exists with that ID.
        """
        await self._delete_resource("storage_paths", id)
