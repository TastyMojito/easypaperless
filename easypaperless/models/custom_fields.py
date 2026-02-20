"""CustomField Pydantic model."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class FieldDataType(StrEnum):
    """Allowed data types for a custom field."""

    string = "string"
    boolean = "boolean"
    integer = "integer"
    float = "float"
    monetary = "monetary"
    date = "date"
    url = "url"
    documentlink = "documentlink"
    select = "select"


class CustomField(BaseModel):
    """A custom field definition in paperless-ngx.

    Attributes:
        id: Unique custom-field ID.
        name: Field name shown in the UI.
        data_type: The value type for this field (see
            :class:`FieldDataType`).
        extra_data: Additional configuration (e.g. select options), or
            ``None``.
        document_count: Number of documents that have a value for this field.
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    data_type: FieldDataType
    extra_data: Any = None
    document_count: int | None = None
