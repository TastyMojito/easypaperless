"""Async resource mixins for PaperlessClient."""

from easypaperless._internal.mixins.correspondents import CorrespondentsMixin
from easypaperless._internal.mixins.custom_fields import CustomFieldsMixin
from easypaperless._internal.mixins.document_bulk import DocumentBulkMixin
from easypaperless._internal.mixins.document_types import DocumentTypesMixin
from easypaperless._internal.mixins.documents import DocumentsMixin
from easypaperless._internal.mixins.non_document_bulk import NonDocumentBulkMixin
from easypaperless._internal.mixins.notes import NotesMixin
from easypaperless._internal.mixins.storage_paths import StoragePathsMixin
from easypaperless._internal.mixins.tags import TagsMixin
from easypaperless._internal.mixins.upload import UploadMixin

__all__ = [
    "DocumentsMixin",
    "NotesMixin",
    "UploadMixin",
    "DocumentBulkMixin",
    "NonDocumentBulkMixin",
    "TagsMixin",
    "CorrespondentsMixin",
    "DocumentTypesMixin",
    "StoragePathsMixin",
    "CustomFieldsMixin",
]
