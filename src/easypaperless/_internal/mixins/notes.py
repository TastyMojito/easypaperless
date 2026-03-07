"""Notes resource mixin for PaperlessClient."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from easypaperless.models.documents import DocumentNote

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession

logger = logging.getLogger(__name__)


class NotesMixin:
    if TYPE_CHECKING:
        _session: HttpSession

    async def get_notes(self, document_id: int) -> list[DocumentNote]:
        """Fetch all notes attached to a document.

        Args:
            document_id: Numeric ID of the document whose notes to retrieve.

        Returns:
            List of :class:`~easypaperless.models.documents.DocumentNote` objects,
            ordered by creation time.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no document exists
                with that ID.
        """
        logger.debug("Fetching notes for document id=%d", document_id)
        resp = await self._session.get(f"/documents/{document_id}/notes/")
        return [DocumentNote.model_validate(item) for item in resp.json()]

    async def create_note(self, document_id: int, *, note: str) -> DocumentNote:
        """Create a new note on a document.

        Args:
            document_id: Numeric ID of the document to annotate.
            note: Text content of the note.

        Returns:
            The newly created :class:`~easypaperless.models.documents.DocumentNote`.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no document exists
                with that ID.
        """
        logger.debug("Creating note for document id=%d", document_id)
        resp = await self._session.post(
            f"/documents/{document_id}/notes/",
            json={"note": note},
        )
        # paperless-ngx returns the full list of notes after creation;
        # the newly created note is the last item in the list.
        data = resp.json()
        if isinstance(data, list):
            return DocumentNote.model_validate(data[-1])
        return DocumentNote.model_validate(data)

    async def delete_note(self, document_id: int, note_id: int) -> None:
        """Delete a note from a document.

        Args:
            document_id: Numeric ID of the document that owns the note.
            note_id: Numeric ID of the note to delete.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no document or note
                exists with the given IDs.
        """
        logger.debug("Deleting note id=%d from document id=%d", note_id, document_id)
        await self._session.delete(f"/documents/{document_id}/notes/", params={"id": note_id})
