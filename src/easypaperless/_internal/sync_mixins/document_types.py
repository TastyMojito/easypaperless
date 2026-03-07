"""Sync document types mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.document_types import DocumentType
from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncDocumentTypesMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def list_document_types(
        self,
        *,
        ids: list[int] | None = None,
        name_contains: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[DocumentType]:
        return self._run(self._async_client.list_document_types(
            ids=ids,
            name_contains=name_contains,
            page=page,
            page_size=page_size,
            ordering=ordering,
            descending=descending,
        ))

    def get_document_type(self, id: int) -> DocumentType:
        return self._run(self._async_client.get_document_type(id))

    def create_document_type(
        self,
        *,
        name: str,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> DocumentType:
        return self._run(self._async_client.create_document_type(
            name=name,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            owner=owner,
            set_permissions=set_permissions,
        ))

    def update_document_type(
        self,
        id: int,
        *,
        name: str | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
    ) -> DocumentType:
        return self._run(self._async_client.update_document_type(
            id,
            name=name,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    def delete_document_type(self, id: int) -> None:
        return self._run(self._async_client.delete_document_type(id))
