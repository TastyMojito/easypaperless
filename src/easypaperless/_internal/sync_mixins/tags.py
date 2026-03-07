"""Sync tags mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.permissions import SetPermissions
from easypaperless.models.tags import Tag

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncTagsMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def list_tags(
        self,
        *,
        ids: list[int] | None = None,
        name_contains: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[Tag]:
        return self._run(self._async_client.list_tags(
            ids=ids,
            name_contains=name_contains,
            page=page,
            page_size=page_size,
            ordering=ordering,
            descending=descending,
        ))

    def get_tag(self, id: int) -> Tag:
        return self._run(self._async_client.get_tag(id))

    def create_tag(
        self,
        *,
        name: str,
        color: str | None = None,
        is_inbox_tag: bool | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        parent: int | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> Tag:
        return self._run(self._async_client.create_tag(
            name=name,
            color=color,
            is_inbox_tag=is_inbox_tag,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            parent=parent,
            owner=owner,
            set_permissions=set_permissions,
        ))

    def update_tag(
        self,
        id: int,
        *,
        name: str | None = None,
        color: str | None = None,
        is_inbox_tag: bool | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        parent: int | None = None,
    ) -> Tag:
        return self._run(self._async_client.update_tag(
            id,
            name=name,
            color=color,
            is_inbox_tag=is_inbox_tag,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            parent=parent,
        ))

    def delete_tag(self, id: int) -> None:
        return self._run(self._async_client.delete_tag(id))
