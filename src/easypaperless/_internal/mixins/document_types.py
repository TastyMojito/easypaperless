"""Document types resource mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.document_types import DocumentType
from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession
    from easypaperless._internal.resolvers import NameResolver


class DocumentTypesMixin:
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

    async def list_document_types(
        self,
        *,
        ids: list[int] | None = None,
        name_contains: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[DocumentType]:
        """Return document types defined in paperless-ngx.

        Args:
            ids: Return only document types whose ID is in this list.
            name_contains: Case-insensitive substring filter on document-type
                name (raw API ``name__icontains``).
            page: Return only this specific page (1-based). Disables
                auto-pagination. Default: ``None`` (return all).
            page_size: Number of results per page. When omitted, the server
                default is used.
            ordering: Field to sort by. Examples: ``"name"``, ``"id"``.
            descending: When ``True``, reverses the sort direction of
                ``ordering``. Ignored when ``ordering`` is ``None``.

        Returns:
            List of
            :class:`~easypaperless.models.document_types.DocumentType`
            objects.
        """
        params: dict[str, Any] = {}
        if ids is not None:
            params["id__in"] = ",".join(str(i) for i in ids)
        if name_contains is not None:
            params["name__icontains"] = name_contains
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if ordering is not None:
            params["ordering"] = f"-{ordering}" if descending else ordering
        return cast(
            list[DocumentType],
            await self._list_resource("document_types", DocumentType, params or None),
        )

    async def get_document_type(self, id: int) -> DocumentType:
        """Fetch a single document type by its ID.

        Args:
            id: Numeric document-type ID.

        Returns:
            The :class:`~easypaperless.models.document_types.DocumentType`
            with the given ID.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no document type
                exists with that ID.
        """
        return cast(DocumentType, await self._get_resource("document_types", id, DocumentType))

    async def create_document_type(
        self,
        *,
        name: str,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> DocumentType:
        """Create a new document type.

        Args:
            name: Document-type name (e.g. ``"Invoice"``, ``"Receipt"``).
                Must be unique.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.
            owner: Numeric user ID to assign as owner. ``None`` creates the
                document type with no owner (visible to all users).
            set_permissions: Explicit view/change permission sets. Defaults to
                no permissions (all users have access via public visibility).

        Returns:
            The newly created
            :class:`~easypaperless.models.document_types.DocumentType`.
        """
        return cast(DocumentType, await self._create_resource(
            "document_types",
            DocumentType,
            owner=owner,
            set_permissions=set_permissions,
            name=name,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    async def update_document_type(
        self,
        id: int,
        *,
        name: str | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
    ) -> DocumentType:
        """Partially update a document type (PATCH semantics).

        Args:
            id: Numeric ID of the document type to update.
            name: Document-type name (e.g. ``"Invoice"``, ``"Receipt"``).
                Must be unique.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.

        Returns:
            The updated
            :class:`~easypaperless.models.document_types.DocumentType`.
        """
        return cast(DocumentType, await self._update_resource(
            "document_types",
            id,
            DocumentType,
            name=name,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    async def delete_document_type(self, id: int) -> None:
        """Delete a document type.

        Args:
            id: Numeric ID of the document type to delete.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no document type
                exists with that ID.
        """
        await self._delete_resource("document_types", id)
