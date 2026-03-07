"""Sync non-document bulk operations mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncNonDocumentBulkMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def bulk_edit_objects(
        self,
        object_type: str,
        object_ids: list[int],
        operation: str,
        **parameters: Any,
    ) -> None:
        return self._run(
            self._async_client.bulk_edit_objects(object_type, object_ids, operation, **parameters)
        )
