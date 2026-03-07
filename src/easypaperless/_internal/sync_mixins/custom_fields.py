"""Sync custom fields mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models.custom_fields import CustomField
from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncCustomFieldsMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def list_custom_fields(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[CustomField]:
        return self._run(self._async_client.list_custom_fields(
            page=page,
            page_size=page_size,
            ordering=ordering,
            descending=descending,
        ))

    def get_custom_field(self, id: int) -> CustomField:
        return self._run(self._async_client.get_custom_field(id))

    def create_custom_field(
        self,
        *,
        name: str,
        data_type: str,
        extra_data: Any | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> CustomField:
        return self._run(self._async_client.create_custom_field(
            name=name,
            data_type=data_type,
            extra_data=extra_data,
            owner=owner,
            set_permissions=set_permissions,
        ))

    def update_custom_field(
        self,
        id: int,
        *,
        name: str | None = None,
        extra_data: Any | None = None,
    ) -> CustomField:
        return self._run(self._async_client.update_custom_field(
            id, name=name, extra_data=extra_data
        ))

    def delete_custom_field(self, id: int) -> None:
        return self._run(self._async_client.delete_custom_field(id))
