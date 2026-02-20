"""Document-related Pydantic models."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    """Status values for a paperless-ngx background processing task."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class Task(BaseModel):
    """A paperless-ngx background processing task (e.g. document ingestion).

    Attributes:
        task_id: Unique Celery task identifier.
        task_file_name: Original file name submitted for processing.
        status: Current task status as a :class:`TaskStatus` enum value.
        result: Human-readable result or error message, set on completion.
        related_document: String representation of the resulting document ID
            on success, ``None`` otherwise.
    """

    model_config = ConfigDict(extra="ignore")

    task_id: str
    task_file_name: str | None = None
    date_created: datetime | None = None
    date_done: datetime | None = None
    type: str | None = None
    status: TaskStatus | None = None
    result: str | None = None
    acknowledged: bool | None = None
    related_document: str | None = None


class SearchHit(BaseModel):
    """Full-text search relevance metadata returned alongside a document.

    Attributes:
        score: Relevance score assigned by the Whoosh FTS engine.
        highlights: HTML snippet with matching terms highlighted.
        rank: Position in the result set by relevance.
    """

    model_config = ConfigDict(extra="ignore")

    score: float | None = None
    highlights: str | None = None
    note_highlights: str | None = None
    rank: int | None = None


class CustomFieldValue(BaseModel):
    """A custom field value attached to a document.

    Attributes:
        field: ID of the :class:`~easypaperless.models.custom_fields.CustomField`
            definition.
        value: The stored value; its Python type depends on the field's
            ``data_type``.
    """

    model_config = ConfigDict(extra="ignore")

    field: int
    value: Any = None


class DocumentNote(BaseModel):
    """A user note attached to a document.

    Attributes:
        id: Unique note ID.
        note: Text content of the note.
        created: Timestamp when the note was created.
        document: ID of the parent document.
        user: ID of the user who created the note.
    """

    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    note: str
    created: datetime | None = None
    document: int | None = None
    user: int | None = None


class Document(BaseModel):
    """A paperless-ngx document.

    Attributes:
        id: Unique document ID.
        title: Document title.
        content: Full OCR text content, if available.
        tags: List of tag IDs assigned to this document.
        document_type: ID of the assigned document type, or ``None``.
        correspondent: ID of the assigned correspondent, or ``None``.
        storage_path: ID of the assigned storage path, or ``None``.
        created: Full creation datetime.
        created_date: Date portion of creation (``date`` object).
        archive_serial_number: Archive serial number (ASN), or ``None``.
        custom_fields: List of :class:`CustomFieldValue` instances.
        notes: User notes attached to this document.
        search_hit: Full-text search relevance metadata, populated only when
            the document was returned by a full-text search.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    title: str
    content: str | None = None
    tags: list[int] = Field(default_factory=list)
    document_type: int | None = None
    correspondent: int | None = None
    storage_path: int | None = None
    created: datetime | None = None
    created_date: date | None = None
    modified: datetime | None = None
    added: datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    owner: int | None = None
    user_can_change: bool | None = None
    is_shared_by_requester: bool | None = None
    notes: list[DocumentNote] = Field(default_factory=list)
    custom_fields: list[CustomFieldValue] = Field(default_factory=list)
    search_hit: SearchHit | None = Field(default=None, alias="__search_hit__")
