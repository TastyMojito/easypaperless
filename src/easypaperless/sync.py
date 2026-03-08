"""Synchronous wrapper around PaperlessClient.

Note: SyncPaperlessClient cannot be used inside an already-running event loop
(e.g., Jupyter notebooks). Use the async PaperlessClient directly there.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any, TypeVar

from easypaperless._internal.sync_mixins import (
    SyncCorrespondentsMixin,
    SyncCustomFieldsMixin,
    SyncDocumentBulkMixin,
    SyncDocumentsMixin,
    SyncDocumentTypesMixin,
    SyncNonDocumentBulkMixin,
    SyncNotesMixin,
    SyncStoragePathsMixin,
    SyncTagsMixin,
    SyncUploadMixin,
)
from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class _SyncCore:
    """Background event loop, _run() helper, and context manager."""

    def __init__(self, url: str, api_key: str, **kwargs: Any) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._async_client = PaperlessClient(url, api_key, **kwargs)

    def _run(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Submit a coroutine to the background event loop and block until done."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def close(self) -> None:
        """Close the underlying HTTP connection pool and stop the event loop.

        Safe to call multiple times — subsequent calls are no-ops.
        """
        if self._loop.is_closed():
            return
        self._run(self._async_client.close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._loop.close()

    def __enter__(self) -> SyncPaperlessClient:
        return self  # type: ignore[return-value]

    def __exit__(self, *args: Any) -> None:
        self.close()


class SyncPaperlessClient(
    SyncDocumentsMixin,
    SyncNotesMixin,
    SyncUploadMixin,
    SyncDocumentBulkMixin,
    SyncNonDocumentBulkMixin,
    SyncTagsMixin,
    SyncCorrespondentsMixin,
    SyncDocumentTypesMixin,
    SyncStoragePathsMixin,
    SyncCustomFieldsMixin,
    _SyncCore,
):
    """Synchronous interface to paperless-ngx.

    Exposes the same methods as
    :class:`~easypaperless.client.PaperlessClient` but runs them
    synchronously, making it suitable for scripts and REPL sessions that do
    not use ``asyncio``.

    All methods have identical signatures to their async counterparts on
    :class:`~easypaperless.client.PaperlessClient`.  Operations run on a
    dedicated background event loop thread so that the httpx connection pool
    is reused across calls and cleanup works correctly.

    Use as a context manager to ensure proper cleanup:

    Example:
        with SyncPaperlessClient(url="http://localhost:8000", api_key="abc") as client:
            tags = client.list_tags()
            docs = client.list_documents(search="invoice")

    Note:
        Cannot be used inside an already-running event loop (e.g. Jupyter
        notebooks).  Use :class:`~easypaperless.client.PaperlessClient`
        directly in those environments.
    """

    # Explicit assignments so pdoc documents these inherited methods.
    # Documents
    list_documents = SyncDocumentsMixin.list_documents
    get_document = SyncDocumentsMixin.get_document
    get_document_metadata = SyncDocumentsMixin.get_document_metadata
    update_document = SyncDocumentsMixin.update_document
    delete_document = SyncDocumentsMixin.delete_document
    download_document = SyncDocumentsMixin.download_document
    # Notes
    get_notes = SyncNotesMixin.get_notes
    create_note = SyncNotesMixin.create_note
    delete_note = SyncNotesMixin.delete_note
    # Upload
    upload_document = SyncUploadMixin.upload_document
    # Document bulk operations
    bulk_edit = SyncDocumentBulkMixin.bulk_edit
    bulk_add_tag = SyncDocumentBulkMixin.bulk_add_tag
    bulk_remove_tag = SyncDocumentBulkMixin.bulk_remove_tag
    bulk_modify_tags = SyncDocumentBulkMixin.bulk_modify_tags
    bulk_delete = SyncDocumentBulkMixin.bulk_delete
    bulk_set_correspondent = SyncDocumentBulkMixin.bulk_set_correspondent
    bulk_set_document_type = SyncDocumentBulkMixin.bulk_set_document_type
    bulk_set_storage_path = SyncDocumentBulkMixin.bulk_set_storage_path
    bulk_modify_custom_fields = SyncDocumentBulkMixin.bulk_modify_custom_fields
    bulk_set_permissions = SyncDocumentBulkMixin.bulk_set_permissions
    # Non-document bulk operations
    bulk_edit_objects = SyncNonDocumentBulkMixin.bulk_edit_objects
    bulk_delete_tags = SyncNonDocumentBulkMixin.bulk_delete_tags
    bulk_delete_correspondents = SyncNonDocumentBulkMixin.bulk_delete_correspondents
    bulk_delete_document_types = SyncNonDocumentBulkMixin.bulk_delete_document_types
    bulk_delete_storage_paths = SyncNonDocumentBulkMixin.bulk_delete_storage_paths
    bulk_set_permissions_tags = SyncNonDocumentBulkMixin.bulk_set_permissions_tags
    bulk_set_permissions_correspondents = SyncNonDocumentBulkMixin.bulk_set_permissions_correspondents
    bulk_set_permissions_document_types = SyncNonDocumentBulkMixin.bulk_set_permissions_document_types
    bulk_set_permissions_storage_paths = SyncNonDocumentBulkMixin.bulk_set_permissions_storage_paths
    # Tags
    list_tags = SyncTagsMixin.list_tags
    get_tag = SyncTagsMixin.get_tag
    create_tag = SyncTagsMixin.create_tag
    update_tag = SyncTagsMixin.update_tag
    delete_tag = SyncTagsMixin.delete_tag
    # Correspondents
    list_correspondents = SyncCorrespondentsMixin.list_correspondents
    get_correspondent = SyncCorrespondentsMixin.get_correspondent
    create_correspondent = SyncCorrespondentsMixin.create_correspondent
    update_correspondent = SyncCorrespondentsMixin.update_correspondent
    delete_correspondent = SyncCorrespondentsMixin.delete_correspondent
    # Document types
    list_document_types = SyncDocumentTypesMixin.list_document_types
    get_document_type = SyncDocumentTypesMixin.get_document_type
    create_document_type = SyncDocumentTypesMixin.create_document_type
    update_document_type = SyncDocumentTypesMixin.update_document_type
    delete_document_type = SyncDocumentTypesMixin.delete_document_type
    # Storage paths
    list_storage_paths = SyncStoragePathsMixin.list_storage_paths
    get_storage_path = SyncStoragePathsMixin.get_storage_path
    create_storage_path = SyncStoragePathsMixin.create_storage_path
    update_storage_path = SyncStoragePathsMixin.update_storage_path
    delete_storage_path = SyncStoragePathsMixin.delete_storage_path
    # Custom fields
    list_custom_fields = SyncCustomFieldsMixin.list_custom_fields
    get_custom_field = SyncCustomFieldsMixin.get_custom_field
    create_custom_field = SyncCustomFieldsMixin.create_custom_field
    update_custom_field = SyncCustomFieldsMixin.update_custom_field
    delete_custom_field = SyncCustomFieldsMixin.delete_custom_field

    def __init__(self, url: str, api_key: str, **kwargs: Any) -> None:
        """Create a synchronous paperless-ngx client.

        Args:
            url: Base URL of the paperless-ngx instance
                (e.g. ``"http://localhost:8000"``).
            api_key: API token.  Generate one in paperless-ngx under
                *Settings → API → Generate Token*.
            **kwargs: Additional keyword arguments forwarded to
                :class:`~easypaperless.client.PaperlessClient` (e.g.
                ``poll_interval``, ``poll_timeout``).
        """
        super().__init__(url, api_key, **kwargs)

    def __enter__(self) -> SyncPaperlessClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

