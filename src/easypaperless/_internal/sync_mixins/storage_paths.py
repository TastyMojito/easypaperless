"""Sync storage paths mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.permissions import SetPermissions
from easypaperless.models.storage_paths import StoragePath

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncStoragePathsMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def list_storage_paths(
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
        return self._run(self._async_client.list_storage_paths(
            ids=ids,
            name_contains=name_contains,
            name_exact=name_exact,
            page=page,
            page_size=page_size,
            ordering=ordering,
            descending=descending,
        ))

    def get_storage_path(self, id: int) -> StoragePath:
        return self._run(self._async_client.get_storage_path(id))

    def create_storage_path(
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
        return self._run(self._async_client.create_storage_path(
            name=name,
            path=path,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            owner=owner,
            set_permissions=set_permissions,
        ))

    def update_storage_path(
        self,
        id: int,
        *,
        name: str | None = None,
        path: str | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
    ) -> StoragePath:
        return self._run(self._async_client.update_storage_path(
            id,
            name=name,
            path=path,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
        ))

    def delete_storage_path(self, id: int) -> None:
        return self._run(self._async_client.delete_storage_path(id))
