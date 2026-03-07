"""Sync upload mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from easypaperless.models.documents import Document

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncUploadMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def upload_document(
        self,
        file: str | Path,
        *,
        title: str | None = None,
        created: str | None = None,
        correspondent: int | str | None = None,
        document_type: int | str | None = None,
        storage_path: int | str | None = None,
        tags: list[int | str] | None = None,
        asn: int | None = None,
        wait: bool = False,
        poll_interval: float | None = None,
        poll_timeout: float | None = None,
    ) -> str | Document:
        return self._run(self._async_client.upload_document(
            file,
            title=title,
            created=created,
            correspondent=correspondent,
            document_type=document_type,
            storage_path=storage_path,
            tags=tags,
            asn=asn,
            wait=wait,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
        ))
