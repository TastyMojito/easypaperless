"""Document bulk operations mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession
    from easypaperless._internal.resolvers import NameResolver


class DocumentBulkMixin:
    if TYPE_CHECKING:
        _session: HttpSession
        _resolver: NameResolver

    async def bulk_edit(
        self, document_ids: list[int], method: str, **parameters: Any
    ) -> None:
        """Execute a bulk-edit operation on a list of documents.

        This is a low-level method; prefer the higher-level helpers such as
        :meth:`bulk_add_tag`, :meth:`bulk_remove_tag`, and
        :meth:`bulk_modify_tags`.

        Args:
            document_ids: List of document IDs to operate on.
            method: Bulk-edit method name as recognised by paperless-ngx
                (e.g. ``"add_tag"``, ``"remove_tag"``, ``"delete"``).
            **parameters: Additional keyword arguments forwarded to the API as
                the ``parameters`` object.
        """
        payload = {"documents": document_ids, "method": method, "parameters": parameters}
        # Use a longer timeout for bulk operations — large batches can take
        # considerably more than the default 30 s on the paperless-ngx side.
        await self._session.post("/documents/bulk_edit/", json=payload, timeout=120.0)

    async def bulk_add_tag(self, document_ids: list[int], tag: int | str) -> None:
        """Add a tag to multiple documents in a single request.

        Args:
            document_ids: List of document IDs to tag.
            tag: Tag to add, as an ID or name.
        """
        tag_id = await self._resolver.resolve("tags", tag)
        await self.bulk_edit(document_ids, "add_tag", tag=tag_id)

    async def bulk_remove_tag(self, document_ids: list[int], tag: int | str) -> None:
        """Remove a tag from multiple documents in a single request.

        Args:
            document_ids: List of document IDs to un-tag.
            tag: Tag to remove, as an ID or name.
        """
        tag_id = await self._resolver.resolve("tags", tag)
        await self.bulk_edit(document_ids, "remove_tag", tag=tag_id)

    async def bulk_modify_tags(
        self,
        document_ids: list[int],
        *,
        add_tags: list[int | str] | None = None,
        remove_tags: list[int | str] | None = None,
    ) -> None:
        """Add and/or remove tags on multiple documents atomically.

        Args:
            document_ids: List of document IDs to modify.
            add_tags: Tags to add, as IDs or names.
            remove_tags: Tags to remove, as IDs or names.
        """
        add_ids = await self._resolver.resolve_list("tags", add_tags or [])
        remove_ids = await self._resolver.resolve_list("tags", remove_tags or [])
        await self.bulk_edit(document_ids, "modify_tags", add_tags=add_ids, remove_tags=remove_ids)

    async def bulk_delete(self, document_ids: list[int]) -> None:
        """Permanently delete multiple documents in a single request.

        Args:
            document_ids: List of document IDs to delete.
        """
        await self.bulk_edit(document_ids, "delete")

    async def bulk_set_correspondent(
        self, document_ids: list[int], correspondent: int | str | None
    ) -> None:
        """Assign a correspondent to multiple documents in a single request.

        Args:
            document_ids: List of document IDs to modify.
            correspondent: Correspondent to assign, as an ID or name.
                Pass ``None`` to clear the assignment.
        """
        cor_id: int | None = None
        if correspondent is not None:
            cor_id = await self._resolver.resolve("correspondents", correspondent)
        await self.bulk_edit(document_ids, "set_correspondent", correspondent=cor_id)

    async def bulk_set_document_type(
        self, document_ids: list[int], document_type: int | str | None
    ) -> None:
        """Assign a document type to multiple documents in a single request.

        Args:
            document_ids: List of document IDs to modify.
            document_type: Document type to assign, as an ID or name.
                Pass ``None`` to clear the assignment.
        """
        dt_id: int | None = None
        if document_type is not None:
            dt_id = await self._resolver.resolve("document_types", document_type)
        await self.bulk_edit(document_ids, "set_document_type", document_type=dt_id)

    async def bulk_set_storage_path(
        self, document_ids: list[int], storage_path: int | str | None
    ) -> None:
        """Assign a storage path to multiple documents in a single request.

        Args:
            document_ids: List of document IDs to modify.
            storage_path: Storage path to assign, as an ID or name.
                Pass ``None`` to clear the assignment.
        """
        sp_id: int | None = None
        if storage_path is not None:
            sp_id = await self._resolver.resolve("storage_paths", storage_path)
        await self.bulk_edit(document_ids, "set_storage_path", storage_path=sp_id)

    async def bulk_modify_custom_fields(
        self,
        document_ids: list[int],
        *,
        add_fields: list[dict[str, Any]] | None = None,
        remove_fields: list[int] | None = None,
    ) -> None:
        """Add and/or remove custom field values on multiple documents.

        Args:
            document_ids: List of document IDs to modify.
            add_fields: Custom-field value dicts to add (each must contain
                ``"field"`` and ``"value"`` keys).
            remove_fields: Custom-field IDs whose values should be removed.
        """
        await self.bulk_edit(
            document_ids,
            "modify_custom_fields",
            add_custom_fields=add_fields or [],
            remove_custom_fields=remove_fields or [],
        )

    async def bulk_set_permissions(
        self,
        document_ids: list[int],
        *,
        set_permissions: SetPermissions | None = None,
        owner: int | None = None,
        merge: bool = False,
    ) -> None:
        """Set permissions and/or owner on multiple documents.

        Args:
            document_ids: List of document IDs to modify.
            set_permissions: Explicit view/change permission sets to apply.
            owner: Numeric user ID to assign as document owner.
            merge: When ``True``, new permissions are merged with existing
                ones rather than replacing them.
        """
        params: dict[str, Any] = {"merge": merge}
        if set_permissions is not None:
            params["set_permissions"] = set_permissions.model_dump()
        if owner is not None:
            params["owner"] = owner
        await self.bulk_edit(document_ids, "set_permissions", **params)
