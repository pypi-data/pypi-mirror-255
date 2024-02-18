import asyncio
from collections.abc import Callable
from contextvars import Context
import io
from typing import Any, Literal
from typing_extensions import Self
from gyver.attrs import mutable, info


@mutable
class MockWriter:
    state: Literal["done", "cancelled", "pending"] = "pending"
    stream: io.BytesIO = info(default_factory=io.BytesIO)
    on_done: list[Callable[[Self], Any]] = info(default_factory=list)

    def add_done_callback(
        self, callback: Callable[[Self], Any], *, context: Context | None = None
    ):
        self.on_done.append(callback)

    def cancel(self):
        self.state = "cancelled"

    async def drain(self):
        return

    async def write(self, chunk: bytes):
        self.stream.write(chunk)

    async def write_eof(self):
        self.stream.close()

    async def enable_compression(self, compress: str):
        del compress

    async def enable_chunking(self):
        pass

    async def write_headers(self, status_line, headers):
        pass

    def __await__(self):
        return self._await().__await__()

    async def _await(self):
        return self
