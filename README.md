# easypaperless

A Python API wrapper for [paperless-ngx](https://docs.paperless-ngx.com/) with an optional SQLite-backed document store for local caching and extended search.

## Installation

```bash
pip install easypaperless
```

From source:

```bash
git clone https://github.com/your-org/easypaperless
cd easypaperless
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Linux / macOS
pip install -e .
```

## Quick start — async

```python
import asyncio
from easypaperless import PaperlessClient

async def main():
    async with PaperlessClient(url="http://localhost:8000", api_key="YOUR_TOKEN") as client:
        # List documents — full-text search across title and OCR content
        docs = await client.list_documents(search="invoice")

        # Fetch a single document
        doc = await client.get_document(42)
        print(doc.title, doc.created_date)

        # Update metadata — string names are resolved to IDs automatically
        await client.update_document(42, tags=["paid"], correspondent="ACME Corp")

        # Upload and wait for processing to complete
        doc = await client.upload_document("scan.pdf", title="April Invoice", wait=True)
        print("Processed:", doc.id)

asyncio.run(main())
```

## Quick start — sync

```python
from easypaperless import SyncPaperlessClient

with SyncPaperlessClient(url="http://localhost:8000", api_key="YOUR_TOKEN") as client:
    tags = client.list_tags()
    docs = client.list_documents(search="receipt", tags=["inbox"])
    client.update_document(docs[0].id, tags=["processed"])
```

> **Note:** `SyncPaperlessClient` cannot be used inside an already-running
> event loop (e.g. Jupyter notebooks). Use `PaperlessClient` directly there.

## DocumentStore — local cache

```python
from easypaperless import PaperlessClient, DocumentStore

async with PaperlessClient(url="http://localhost:8000", api_key="YOUR_TOKEN") as client:
    store = DocumentStore(client, db_path="paperless.db")

    # Pull all data from the server into SQLite
    count = await store.sync()
    print(f"Synced {count} documents")

    # Search locally — no network request
    results = store.search_documents(
        tags=["invoice"],
        created_after="2024-01-01",
        title_regex=r"Q[1-4]\s+\d{4}",  # Python regex on title
    )
    store.close()
```

## Logging

`easypaperless` uses the standard `logging` module under the `easypaperless` logger hierarchy.

```python
import logging

logging.basicConfig(level=logging.WARNING)          # default — warnings only
logging.getLogger("easypaperless").setLevel(logging.INFO)   # upload/sync progress
logging.getLogger("easypaperless").setLevel(logging.DEBUG)  # full request detail
```

| Level | What you see |
|-------|--------------|
| `WARNING` | Task failures, timeouts |
| `INFO` | Upload/sync progress, document counts |
| `DEBUG` | Every HTTP request, task polling, SQL queries |

## API reference

Generate the full HTML reference locally:

```bash
pip install -e ".[docs]"
pdoc easypaperless -o docs/
# open docs/easypaperless.html
```

Or browse interactively while writing code:

```bash
pdoc easypaperless
# serves at http://localhost:8080
```
