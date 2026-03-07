"""Sync notes mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models.documents import DocumentNote

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncNotesMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def get_notes(self, document_id: int) -> list[DocumentNote]:
        return self._run(self._async_client.get_notes(document_id))

    def create_note(self, document_id: int, *, note: str) -> DocumentNote:
        return self._run(self._async_client.create_note(document_id, note=note))

    def delete_note(self, document_id: int, note_id: int) -> None:
        return self._run(self._async_client.delete_note(document_id, note_id))
