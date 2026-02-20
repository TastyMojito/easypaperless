"""
examples.py — easypaperless usage examples covering all endpoints.

Setup:
    1. Copy .env.EXAMPLE to .env and fill in your credentials.
    2. Activate the venv and install script dependencies:
           pip install -e ".[scripts]"
    3. Run:
           python scripts/examples.py

Notes:
    - Read-only operations run automatically.
    - Mutating operations (create, update, delete, upload, bulk edit) are
      commented out so you don't accidentally modify your paperless instance.
      Uncomment the lines you want to try.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from easypaperless import PaperlessClient, SyncPaperlessClient

# Load credentials from .env (file is git-ignored — never committed).
load_dotenv(Path(__file__).parent.parent / ".env")

PAPERLESS_URL = os.environ["PAPERLESS_URL"]
PAPERLESS_API_KEY = os.environ["PAPERLESS_API_KEY"]


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


async def demo_documents(client: PaperlessClient) -> None:
    print("\n=== Documents ===")

    # List all documents
    docs = await client.list_documents()
    print(f"Total documents: {len(docs)}")

    if not docs:
        print("No documents found — skipping document examples.")
        return

    first = docs[0]
    print(f"First document: [{first.id}] {first.title!r}")

    # Get a single document by ID
    doc = await client.get_document(first.id)
    print(f"Fetched by ID: {doc.title!r}, created: {doc.created}")

    # Search — title only (fast, uses database index)
    results = await client.list_documents(search="invoice", search_mode="title")
    print(f"Title search 'invoice': {len(results)} hit(s)")

    # Search — title + OCR text (default; uses Whoosh full-text index)
    results = await client.list_documents(search="invoice", search_mode="title_or_text")
    print(f"Full-text search 'invoice': {len(results)} hit(s)")

    # Search — raw paperless query language
    results = await client.list_documents(
        search="tag:invoice date:[2024 TO *]", search_mode="query"
    )
    print(f"Query search: {len(results)} hit(s)")

    # Filter by date range (ISO 8601 strings)
    results = await client.list_documents(
        created_after="2024-01-01", created_before="2024-12-31"
    )
    print(f"Documents created in 2024: {len(results)}")

    # Filter by tag names (all tags must be present; names are resolved to IDs)
    # results = await client.list_documents(tags=["invoice", "bank"])
    # print(f"Tagged 'invoice' AND 'bank': {len(results)}")

    # Filter by any tag (at least one must be present)
    # results = await client.list_documents(any_tag=["invoice", "receipt"])
    # print(f"Tagged 'invoice' OR 'receipt': {len(results)}")

    # Filter by correspondent and document type (names or IDs both work)
    # results = await client.list_documents(
    #     correspondent="ACME Corp",
    #     document_type="Invoice",
    # )
    # print(f"ACME invoices: {len(results)}")

    # Update a document — only fields you pass are changed (PATCH)
    # updated = await client.update_document(
    #     first.id,
    #     title="Renamed via easypaperless",
    #     tags=["invoice"],           # tag names resolved to IDs automatically
    #     correspondent="ACME Corp",
    # )
    # print(f"Updated title: {updated.title!r}")

    # Download the archived PDF
    # pdf_bytes = await client.download_document(first.id)
    # Path("downloaded.pdf").write_bytes(pdf_bytes)
    # print(f"Downloaded {len(pdf_bytes):,} bytes")

    # Download the original file instead of the archived PDF
    # original_bytes = await client.download_document(first.id, original=True)

    # Delete a document permanently
    # await client.delete_document(first.id)
    # print("Deleted document")


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


async def demo_upload(client: PaperlessClient) -> None:
    print("\n=== Upload ===")

    # Submit a file and get back the task ID immediately (non-blocking)
    # task_id = await client.upload_document("scan.pdf", title="April Invoice")
    # print(f"Submitted, task ID: {task_id}")

    # Submit and wait until paperless finishes processing — returns a Document
    # doc = await client.upload_document(
    #     "scan.pdf",
    #     title="April Invoice",
    #     tags=["invoice", "bank"],       # names resolved automatically
    #     correspondent="ACME Corp",
    #     document_type="Invoice",
    #     created="2024-04-01",
    #     wait=True,
    #     poll_timeout=120.0,             # seconds before TaskTimeoutError
    # )
    # print(f"Processed: [{doc.id}] {doc.title!r}")

    print("(upload examples are commented out — replace 'scan.pdf' with a real path)")


# ---------------------------------------------------------------------------
# Bulk operations
# ---------------------------------------------------------------------------


async def demo_bulk(client: PaperlessClient) -> None:
    print("\n=== Bulk operations ===")

    docs = await client.list_documents()
    if len(docs) < 2:
        print("Need at least 2 documents to show bulk examples — skipping.")
        return

    ids = [d.id for d in docs[:2]]
    print(f"Would operate on document IDs: {ids}")

    # Add the same tag to multiple documents at once
    # await client.bulk_add_tag(ids, "reviewed")
    # print("Added tag 'reviewed' to all")

    # Remove a tag from multiple documents
    # await client.bulk_remove_tag(ids, "reviewed")
    # print("Removed tag 'reviewed'")

    # Add and remove multiple tags in one request
    # await client.bulk_modify_tags(ids, add_tags=["important"], remove_tags=["draft"])

    # Delete multiple documents permanently — use with care
    # await client.bulk_delete(ids)
    # print("Bulk deleted")

    # Bulk edit arbitrary objects (tags, correspondents, etc.) via the raw endpoint
    # await client.bulk_edit_objects(
    #     object_type="tags",
    #     object_ids=[1, 2],
    #     operation="delete",
    # )

    print("(bulk edit examples are commented out to avoid accidental changes)")


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


async def demo_tags(client: PaperlessClient) -> None:
    print("\n=== Tags ===")

    tags = await client.list_tags()
    print(f"Total tags: {len(tags)}")
    for tag in tags[:5]:
        print(f"  [{tag.id}] {tag.name!r}  (color: {tag.colour})")

    if tags:
        tag = await client.get_tag(tags[0].id)
        print(f"Fetched by ID: {tag.name!r}")

    # Create a new tag
    # new_tag = await client.create_tag(name="easypaperless-demo")
    # print(f"Created: [{new_tag.id}] {new_tag.name!r}")

    # Rename it
    # updated = await client.update_tag(new_tag.id, name="easypaperless-demo-renamed")
    # print(f"Renamed to: {updated.name!r}")

    # Delete it
    # await client.delete_tag(new_tag.id)
    # print("Deleted tag")


# ---------------------------------------------------------------------------
# Correspondents
# ---------------------------------------------------------------------------


async def demo_correspondents(client: PaperlessClient) -> None:
    print("\n=== Correspondents ===")

    correspondents = await client.list_correspondents()
    print(f"Total correspondents: {len(correspondents)}")
    for c in correspondents[:5]:
        print(f"  [{c.id}] {c.name!r}")

    if correspondents:
        c = await client.get_correspondent(correspondents[0].id)
        print(f"Fetched by ID: {c.name!r}")

    # new = await client.create_correspondent(name="Example Corp")
    # print(f"Created: [{new.id}] {new.name!r}")

    # updated = await client.update_correspondent(new.id, name="Example Corp (renamed)")
    # print(f"Renamed: {updated.name!r}")

    # await client.delete_correspondent(new.id)
    # print("Deleted")


# ---------------------------------------------------------------------------
# Document Types
# ---------------------------------------------------------------------------


async def demo_document_types(client: PaperlessClient) -> None:
    print("\n=== Document Types ===")

    types = await client.list_document_types()
    print(f"Total document types: {len(types)}")
    for dt in types[:5]:
        print(f"  [{dt.id}] {dt.name!r}")

    if types:
        dt = await client.get_document_type(types[0].id)
        print(f"Fetched by ID: {dt.name!r}")

    # new = await client.create_document_type(name="Demo Type")
    # print(f"Created: [{new.id}] {new.name!r}")

    # updated = await client.update_document_type(new.id, name="Demo Type (renamed)")
    # print(f"Renamed: {updated.name!r}")

    # await client.delete_document_type(new.id)
    # print("Deleted")


# ---------------------------------------------------------------------------
# Storage Paths
# ---------------------------------------------------------------------------


async def demo_storage_paths(client: PaperlessClient) -> None:
    print("\n=== Storage Paths ===")

    paths = await client.list_storage_paths()
    print(f"Total storage paths: {len(paths)}")
    for sp in paths[:5]:
        print(f"  [{sp.id}] {sp.name!r}")

    if paths:
        sp = await client.get_storage_path(paths[0].id)
        print(f"Fetched by ID: {sp.name!r}")

    # Storage path strings use paperless template syntax, e.g. "{correspondent}/{title}"
    # new = await client.create_storage_path(name="Demo Path", path="{title}")
    # print(f"Created: [{new.id}] {new.name!r}")

    # updated = await client.update_storage_path(new.id, name="Demo Path (renamed)")
    # print(f"Renamed: {updated.name!r}")

    # await client.delete_storage_path(new.id)
    # print("Deleted")


# ---------------------------------------------------------------------------
# Custom Fields
# ---------------------------------------------------------------------------


async def demo_custom_fields(client: PaperlessClient) -> None:
    print("\n=== Custom Fields ===")

    fields = await client.list_custom_fields()
    print(f"Total custom fields: {len(fields)}")
    for f in fields[:5]:
        print(f"  [{f.id}] {f.name!r}  (type: {f.data_type})")

    if fields:
        field = await client.get_custom_field(fields[0].id)
        print(f"Fetched by ID: {field.name!r}, data_type: {field.data_type!r}")

    # Valid data_type values: "string", "integer", "float", "monetary",
    #                         "date", "boolean", "url", "document_link"
    # new = await client.create_custom_field(name="Due Date", data_type="date")
    # print(f"Created: [{new.id}] {new.name!r}")

    # updated = await client.update_custom_field(new.id, name="Due Date (renamed)")
    # print(f"Renamed: {updated.name!r}")

    # Assign a custom field value when updating a document:
    # updated_doc = await client.update_document(
    #     doc_id,
    #     custom_fields=[{"field": new.id, "value": "2024-12-31"}],
    # )

    # await client.delete_custom_field(new.id)
    # print("Deleted")


# ---------------------------------------------------------------------------
# Sync client — no asyncio needed
# ---------------------------------------------------------------------------


def demo_sync_client() -> None:
    print("\n=== Sync client ===")

    with SyncPaperlessClient(url=PAPERLESS_URL, api_key=PAPERLESS_API_KEY) as client:
        tags = client.list_tags()
        print(f"Tags via sync client: {len(tags)}")

        docs = client.list_documents(search="invoice", search_mode="title")
        print(f"Invoice search via sync client: {len(docs)} hit(s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    async with PaperlessClient(url=PAPERLESS_URL, api_key=PAPERLESS_API_KEY) as client:
        await demo_documents(client)
        await demo_upload(client)
        await demo_bulk(client)
        await demo_tags(client)
        await demo_correspondents(client)
        await demo_document_types(client)
        await demo_storage_paths(client)
        await demo_custom_fields(client)

    demo_sync_client()

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
