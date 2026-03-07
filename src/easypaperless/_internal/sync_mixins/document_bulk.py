"""Sync document bulk operations mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncDocumentBulkMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def bulk_edit(self, document_ids: list[int], method: str, **parameters: Any) -> None:
        return self._run(self._async_client.bulk_edit(document_ids, method, **parameters))

    def bulk_add_tag(self, document_ids: list[int], tag: int | str) -> None:
        return self._run(self._async_client.bulk_add_tag(document_ids, tag))

    def bulk_remove_tag(self, document_ids: list[int], tag: int | str) -> None:
        return self._run(self._async_client.bulk_remove_tag(document_ids, tag))

    def bulk_modify_tags(
        self,
        document_ids: list[int],
        *,
        add_tags: list[int | str] | None = None,
        remove_tags: list[int | str] | None = None,
    ) -> None:
        return self._run(self._async_client.bulk_modify_tags(
            document_ids, add_tags=add_tags, remove_tags=remove_tags
        ))

    def bulk_delete(self, document_ids: list[int]) -> None:
        return self._run(self._async_client.bulk_delete(document_ids))

    def bulk_set_correspondent(
        self, document_ids: list[int], correspondent: int | str | None
    ) -> None:
        return self._run(
            self._async_client.bulk_set_correspondent(document_ids, correspondent)
        )

    def bulk_set_document_type(
        self, document_ids: list[int], document_type: int | str | None
    ) -> None:
        return self._run(
            self._async_client.bulk_set_document_type(document_ids, document_type)
        )

    def bulk_set_storage_path(
        self, document_ids: list[int], storage_path: int | str | None
    ) -> None:
        return self._run(
            self._async_client.bulk_set_storage_path(document_ids, storage_path)
        )

    def bulk_modify_custom_fields(
        self,
        document_ids: list[int],
        *,
        add_fields: list[dict[str, Any]] | None = None,
        remove_fields: list[int] | None = None,
    ) -> None:
        return self._run(
            self._async_client.bulk_modify_custom_fields(
                document_ids, add_fields=add_fields, remove_fields=remove_fields
            )
        )

    def bulk_set_permissions(
        self,
        document_ids: list[int],
        *,
        set_permissions: SetPermissions | None = None,
        owner: int | None = None,
        merge: bool = False,
    ) -> None:
        return self._run(
            self._async_client.bulk_set_permissions(
                document_ids,
                set_permissions=set_permissions,
                owner=owner,
                merge=merge,
            )
        )
