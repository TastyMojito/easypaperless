"""Sync resource mixins for SyncPaperlessClient."""

from easypaperless._internal.sync_mixins.correspondents import SyncCorrespondentsMixin
from easypaperless._internal.sync_mixins.custom_fields import SyncCustomFieldsMixin
from easypaperless._internal.sync_mixins.document_bulk import SyncDocumentBulkMixin
from easypaperless._internal.sync_mixins.document_types import SyncDocumentTypesMixin
from easypaperless._internal.sync_mixins.documents import SyncDocumentsMixin
from easypaperless._internal.sync_mixins.non_document_bulk import SyncNonDocumentBulkMixin
from easypaperless._internal.sync_mixins.notes import SyncNotesMixin
from easypaperless._internal.sync_mixins.storage_paths import SyncStoragePathsMixin
from easypaperless._internal.sync_mixins.tags import SyncTagsMixin
from easypaperless._internal.sync_mixins.upload import SyncUploadMixin

__all__ = [
    "SyncDocumentsMixin",
    "SyncNotesMixin",
    "SyncUploadMixin",
    "SyncDocumentBulkMixin",
    "SyncNonDocumentBulkMixin",
    "SyncTagsMixin",
    "SyncCorrespondentsMixin",
    "SyncDocumentTypesMixin",
    "SyncStoragePathsMixin",
    "SyncCustomFieldsMixin",
]
