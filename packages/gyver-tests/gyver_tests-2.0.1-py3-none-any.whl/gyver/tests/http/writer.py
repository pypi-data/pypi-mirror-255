import asyncio
from unittest.mock import Mock
from gyver.attrs import mutable


@mutable
class MockWriter:
    def __await__(self):
        return self._await()

    async def _await(self):
        pass

    @classmethod
    def create(cls):
        return asyncio.ensure_future(cls())
