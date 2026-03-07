"""Non-document bulk operations mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from easypaperless.models.correspondents import Correspondent
from easypaperless.models.custom_fields import CustomField
from easypaperless.models.document_types import DocumentType
from easypaperless.models.storage_paths import StoragePath
from easypaperless.models.tags import Tag

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession

_RESOURCE_MODELS = {
    "tags": Tag,
    "correspondents": Correspondent,
    "document_types": DocumentType,
    "storage_paths": StoragePath,
    "custom_fields": CustomField,
}


class NonDocumentBulkMixin:
    if TYPE_CHECKING:
        _session: HttpSession

    async def bulk_edit_objects(
        self,
        object_type: str,
        object_ids: list[int],
        operation: str,
        **parameters: Any,
    ) -> None:
        """Execute a bulk operation on non-document objects (tags, etc.).

        Args:
            object_type: The paperless-ngx object type string (e.g.
                ``"tags"``, ``"correspondents"``).
            object_ids: List of object IDs to operate on.
            operation: Operation name recognised by the
                ``/bulk_edit_objects/`` endpoint.
            **parameters: Additional keyword arguments forwarded directly to
                the API payload.
        """
        payload = {
            "objects": object_ids,
            "object_type": object_type,
            "operation": operation,
            **parameters,
        }
        await self._session.post("/bulk_edit_objects/", json=payload)
