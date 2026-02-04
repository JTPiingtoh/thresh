import aiohttp
import asyncio

from contextlib import asynccontextmanager

from typing import Final, AsyncIterator, AsyncContextManager



class SomeOtherClient():

    _connection: Final

    def __init__(self, connection):
        self._connection = connection


    @AsyncContextManager
    @classmethod
    async def connect(cls) -> AsyncIterator:
        connection: ... # Final[connection]
        try:
            yield connection 
        finally:
            # _disconnect()
            ...