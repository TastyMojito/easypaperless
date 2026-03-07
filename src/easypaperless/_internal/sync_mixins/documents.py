"""Sync documents mixin."""

from __future__ import annotations

from collections.abc import Coroutine
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from easypaperless.models.documents import Document, DocumentMetadata
from easypaperless.models.permissions import SetPermissions

if TYPE_CHECKING:
    from easypaperless.client import PaperlessClient

_T = TypeVar("_T")


class SyncDocumentsMixin:
    if TYPE_CHECKING:
        _async_client: PaperlessClient

        def _run(self, coro: Coroutine[Any, Any, _T]) -> _T: ...

    def get_document(self, id: int, *, include_metadata: bool = False) -> Document:
        return self._run(self._async_client.get_document(id, include_metadata=include_metadata))

    def get_document_metadata(self, id: int) -> DocumentMetadata:
        return self._run(self._async_client.get_document_metadata(id))

    def list_documents(
        self,
        *,
        search: str | None = None,
        search_mode: str = "title_or_text",
        ids: list[int] | None = None,
        tags: list[int | str] | None = None,
        any_tags: list[int | str] | None = None,
        exclude_tags: list[int | str] | None = None,
        correspondent: int | str | None = None,
        any_correspondent: list[int | str] | None = None,
        exclude_correspondents: list[int | str] | None = None,
        document_type: int | str | None = None,
        any_document_type: list[int | str] | None = None,
        exclude_document_types: list[int | str] | None = None,
        storage_path: int | str | None = None,
        any_storage_paths: list[int | str] | None = None,
        exclude_storage_paths: list[int | str] | None = None,
        owner: int | None = None,
        exclude_owners: list[int] | None = None,
        custom_fields: list[int | str] | None = None,
        any_custom_fields: list[int | str] | None = None,
        exclude_custom_fields: list[int | str] | None = None,
        custom_field_query: list[Any] | None = None,
        archive_serial_number: int | None = None,
        archive_serial_number_from: int | None = None,
        archive_serial_number_till: int | None = None,
        created_after: date | str | None = None,
        created_before: date | str | None = None,
        added_after: date | datetime | str | None = None,
        added_from: date | datetime | str | None = None,
        added_before: date | datetime | str | None = None,
        added_until: date | datetime | str | None = None,
        modified_after: date | datetime | str | None = None,
        modified_from: date | datetime | str | None = None,
        modified_before: date | datetime | str | None = None,
        modified_until: date | datetime | str | None = None,
        checksum: str | None = None,
        page_size: int = 25,
        page: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
        max_results: int | None = None,
        on_page: Callable[[int, int | None], None] | None = None,
    ) -> list[Document]:
        return self._run(self._async_client.list_documents(
            search=search,
            search_mode=search_mode,
            ids=ids,
            tags=tags,
            any_tags=any_tags,
            exclude_tags=exclude_tags,
            correspondent=correspondent,
            any_correspondent=any_correspondent,
            exclude_correspondents=exclude_correspondents,
            document_type=document_type,
            any_document_type=any_document_type,
            exclude_document_types=exclude_document_types,
            storage_path=storage_path,
            any_storage_paths=any_storage_paths,
            exclude_storage_paths=exclude_storage_paths,
            owner=owner,
            exclude_owners=exclude_owners,
            custom_fields=custom_fields,
            any_custom_fields=any_custom_fields,
            exclude_custom_fields=exclude_custom_fields,
            custom_field_query=custom_field_query,
            archive_serial_number=archive_serial_number,
            archive_serial_number_from=archive_serial_number_from,
            archive_serial_number_till=archive_serial_number_till,
            created_after=created_after,
            created_before=created_before,
            added_after=added_after,
            added_from=added_from,
            added_before=added_before,
            added_until=added_until,
            modified_after=modified_after,
            modified_from=modified_from,
            modified_before=modified_before,
            modified_until=modified_until,
            checksum=checksum,
            page_size=page_size,
            page=page,
            ordering=ordering,
            descending=descending,
            max_results=max_results,
            on_page=on_page,
        ))

    def update_document(
        self,
        id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        date: str | None = None,
        correspondent: int | str | None = None,
        document_type: int | str | None = None,
        storage_path: int | str | None = None,
        tags: list[int | str] | None = None,
        asn: int | None = None,
        custom_fields: list[dict[str, Any]] | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> Document:
        return self._run(self._async_client.update_document(
            id,
            title=title,
            content=content,
            date=date,
            correspondent=correspondent,
            document_type=document_type,
            storage_path=storage_path,
            tags=tags,
            asn=asn,
            custom_fields=custom_fields,
            owner=owner,
            set_permissions=set_permissions,
        ))

    def delete_document(self, id: int) -> None:
        return self._run(self._async_client.delete_document(id))

    def download_document(self, id: int, *, original: bool = False) -> bytes:
        return self._run(self._async_client.download_document(id, original=original))
