"""Synchronous wrapper around PaperlessClient.

Note: SyncPaperlessClient cannot be used inside an already-running event loop
(e.g., Jupyter notebooks). Use the async PaperlessClient directly there.
"""

from __future__ import annotations

import asyncio
import inspect
import threading
from typing import Any

from easypaperless.client import PaperlessClient


class SyncPaperlessClient:
    """Synchronous interface to paperless-ngx.

    All async methods of PaperlessClient are available here with the same
    signatures. Operations run on a dedicated background event loop thread so
    that the httpx connection pool is reused across calls and cleanup works
    correctly — unlike asyncio.run(), which creates and destroys a loop per
    call and leaves transports in a broken state on the next call.

    No business logic lives here.
    """

    def __init__(self, url: str, api_key: str, **kwargs: Any) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._async_client = PaperlessClient(url, api_key, **kwargs)

    def _run(self, coro: Any) -> Any:
        """Submit a coroutine to the background event loop and block until done."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._async_client, name)
        if inspect.iscoroutinefunction(attr):
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self._run(attr(*args, **kwargs))
            wrapper.__name__ = name
            return wrapper
        return attr

    def close(self) -> None:
        self._run(self._async_client.close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._loop.close()

    def __enter__(self) -> SyncPaperlessClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
