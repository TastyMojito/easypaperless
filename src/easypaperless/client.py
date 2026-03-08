"""Async PaperlessClient — the primary public interface."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

from easypaperless._internal.http import HttpSession
from ._internal.mixins import (
    CorrespondentsMixin,
    CustomFieldsMixin,
    DocumentBulkMixin,
    DocumentsMixin,
    DocumentTypesMixin,
    NonDocumentBulkMixin,
    NotesMixin,
    StoragePathsMixin,
    TagsMixin,
    UploadMixin,
)
from easypaperless._internal.resolvers import NameResolver
from easypaperless.models.permissions import SetPermissions


class _ClientCore:
    """Base class: constructor, context manager, and internal CRUD helpers."""

    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        timeout: float = 30.0,
        poll_interval: float = 2.0,
        poll_timeout: float = 60.0,
    ) -> None:
        self._session = HttpSession(base_url=url, api_key=api_key, timeout=timeout)
        self._resolver = NameResolver(self._session)
        self._poll_interval = poll_interval
        self._poll_timeout = poll_timeout

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._session.close()

    async def __aenter__(self) -> PaperlessClient:
        return self  # type: ignore[return-value]

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _list_resource(
        self,
        resource: str,
        model_class: type[Any],
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        if params and "page" in params:
            resp = await self._session.get(f"/{resource}/", params=params)
            items = resp.json().get("results", [])
        else:
            items = await self._session.get_all_pages(f"/{resource}/", params)
        return [model_class.model_validate(item) for item in items]

    async def _get_resource(self, resource: str, id: int, model_class: type[Any]) -> Any:
        resp = await self._session.get(f"/{resource}/{id}/")
        return model_class.model_validate(resp.json())

    async def _create_resource(
        self,
        resource: str,
        model_class: type[Any],
        *,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
        **kwargs: Any,
    ) -> Any:
        logger.debug("Creating %s resource", resource)
        payload = {k: v for k, v in kwargs.items() if v is not None}
        payload["owner"] = owner  # always send, even as null
        payload["set_permissions"] = (
            set_permissions if set_permissions is not None else SetPermissions()
        ).model_dump()
        resp = await self._session.post(f"/{resource}/", json=payload)
        self._resolver.invalidate(resource)
        return model_class.model_validate(resp.json())

    async def _update_resource(
        self, resource: str, id: int, model_class: type[Any], **kwargs: Any
    ) -> Any:
        logger.debug("Updating %s resource id=%d", resource, id)
        payload = {k: v for k, v in kwargs.items() if v is not None}
        resp = await self._session.patch(f"/{resource}/{id}/", json=payload)
        self._resolver.invalidate(resource)
        return model_class.model_validate(resp.json())

    async def _delete_resource(self, resource: str, id: int) -> None:
        logger.debug("Deleting %s resource id=%d", resource, id)
        await self._session.delete(f"/{resource}/{id}/")
        self._resolver.invalidate(resource)

class PaperlessClient(
    DocumentsMixin,
    NotesMixin,
    UploadMixin,
    DocumentBulkMixin,
    NonDocumentBulkMixin,
    TagsMixin,
    CorrespondentsMixin,
    DocumentTypesMixin,
    StoragePathsMixin,
    CustomFieldsMixin,
    _ClientCore,
):
    """Async client for the paperless-ngx API.

    All operations are flat methods on the client.  String names are resolved
    to integer IDs automatically wherever the API requires IDs (tags,
    correspondents, document types, storage paths).

    Use as an async context manager to ensure the underlying HTTP connection
    pool is closed when you are done:

    Example:
        async with PaperlessClient(url="http://localhost:8000", api_key="abc") as client:
            docs = await client.list_documents()
    """

    # Explicit assignments so pdoc documents these inherited methods.
    # Documents
    list_documents = DocumentsMixin.list_documents
    get_document = DocumentsMixin.get_document
    get_document_metadata = DocumentsMixin.get_document_metadata
    update_document = DocumentsMixin.update_document
    delete_document = DocumentsMixin.delete_document
    download_document = DocumentsMixin.download_document
    # Notes
    get_notes = NotesMixin.get_notes
    create_note = NotesMixin.create_note
    delete_note = NotesMixin.delete_note
    # Upload
    upload_document = UploadMixin.upload_document
    # Document bulk operations
    bulk_edit = DocumentBulkMixin.bulk_edit
    bulk_add_tag = DocumentBulkMixin.bulk_add_tag
    bulk_remove_tag = DocumentBulkMixin.bulk_remove_tag
    bulk_modify_tags = DocumentBulkMixin.bulk_modify_tags
    bulk_delete = DocumentBulkMixin.bulk_delete
    bulk_set_correspondent = DocumentBulkMixin.bulk_set_correspondent
    bulk_set_document_type = DocumentBulkMixin.bulk_set_document_type
    bulk_set_storage_path = DocumentBulkMixin.bulk_set_storage_path
    bulk_modify_custom_fields = DocumentBulkMixin.bulk_modify_custom_fields
    bulk_set_permissions = DocumentBulkMixin.bulk_set_permissions
    # Non-document bulk operations
    bulk_edit_objects = NonDocumentBulkMixin.bulk_edit_objects
    bulk_delete_tags = NonDocumentBulkMixin.bulk_delete_tags
    bulk_delete_correspondents = NonDocumentBulkMixin.bulk_delete_correspondents
    bulk_delete_document_types = NonDocumentBulkMixin.bulk_delete_document_types
    bulk_delete_storage_paths = NonDocumentBulkMixin.bulk_delete_storage_paths
    bulk_set_permissions_tags = NonDocumentBulkMixin.bulk_set_permissions_tags
    bulk_set_permissions_correspondents = NonDocumentBulkMixin.bulk_set_permissions_correspondents
    bulk_set_permissions_document_types = NonDocumentBulkMixin.bulk_set_permissions_document_types
    bulk_set_permissions_storage_paths = NonDocumentBulkMixin.bulk_set_permissions_storage_paths
    # Tags
    list_tags = TagsMixin.list_tags
    get_tag = TagsMixin.get_tag
    create_tag = TagsMixin.create_tag
    update_tag = TagsMixin.update_tag
    delete_tag = TagsMixin.delete_tag
    # Correspondents
    list_correspondents = CorrespondentsMixin.list_correspondents
    get_correspondent = CorrespondentsMixin.get_correspondent
    create_correspondent = CorrespondentsMixin.create_correspondent
    update_correspondent = CorrespondentsMixin.update_correspondent
    delete_correspondent = CorrespondentsMixin.delete_correspondent
    # Document types
    list_document_types = DocumentTypesMixin.list_document_types
    get_document_type = DocumentTypesMixin.get_document_type
    create_document_type = DocumentTypesMixin.create_document_type
    update_document_type = DocumentTypesMixin.update_document_type
    delete_document_type = DocumentTypesMixin.delete_document_type
    # Storage paths
    list_storage_paths = StoragePathsMixin.list_storage_paths
    get_storage_path = StoragePathsMixin.get_storage_path
    create_storage_path = StoragePathsMixin.create_storage_path
    update_storage_path = StoragePathsMixin.update_storage_path
    delete_storage_path = StoragePathsMixin.delete_storage_path
    # Custom fields
    list_custom_fields = CustomFieldsMixin.list_custom_fields
    get_custom_field = CustomFieldsMixin.get_custom_field
    create_custom_field = CustomFieldsMixin.create_custom_field
    update_custom_field = CustomFieldsMixin.update_custom_field
    delete_custom_field = CustomFieldsMixin.delete_custom_field



    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        timeout: float = 30.0,
        poll_interval: float = 2.0,
        poll_timeout: float = 60.0,
    ) -> None:
        """Create an async paperless-ngx client.

        Args:
            url: Base URL of the paperless-ngx instance
                (e.g. ``"http://localhost:8000"``).
            api_key: API token.  Generate one in paperless-ngx under
                *Settings → API → Generate Token*.
            timeout: Default request timeout in seconds.  Individual
                operations (e.g. uploads) may override this per-call.
                Default: ``30.0``.
            poll_interval: Seconds between status checks when ``wait=True``
                is passed to :meth:`upload_document`.  Default: ``2.0``.
            poll_timeout: Maximum seconds to wait for a document to finish
                processing before raising
                :exc:`~easypaperless.exceptions.TaskTimeoutError`.
                Default: ``60.0``.
        """
        super().__init__(
            url, api_key, timeout=timeout, poll_interval=poll_interval, poll_timeout=poll_timeout
        )

    async def __aenter__(self) -> PaperlessClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

