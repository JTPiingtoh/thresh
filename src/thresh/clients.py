import aiohttp
import asyncio

from contextlib import asynccontextmanager

from typing import Final, AsyncIterator, AsyncContextManager



class RiotAPIClient():

    _session: Final

    def __init__(self, session):
        self._session = session

    @classmethod
    @asynccontextmanager
    async def connect(cls) -> AsyncIterator:

        session: aiohttp.ClientSession = aiohttp.ClientSession()
        try:
            yield cls(session) 
        finally:

            # Handle https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-592596034
            # 
            transports = 0
            all_is_lost = asyncio.Event()
            if len(session.connector._conns) == 0:
                all_is_lost.set()
            for conn in session.connector._conns.values():
                for handler, _ in conn:
                    proto : asyncio.Protocol = getattr(handler.transport, "_ssl_protocol", None)
                    if proto is None:
                        continue

                    transports += 1
                    orig_lost = proto.connection_lost
                    orig_eof_recieved = proto.eof_received

                    def connection_lost(exc):
                        orig_lost(exc)
                        nonlocal transports
                        transports -= 1
                        if transports == 0:
                            all_is_lost.set()

                    def eof_recieved():
                        try:
                            orig_eof_recieved()
                        
                        # handle case were eof_recieved is called after 
                        # _app_protocol and _transport are set to None.
                        except AttributeError:
                            pass


    async def get_from_test_url(self):
        await asyncio.sleep(0)



if __name__ == "__main__":

    async def main():
        async with RiotAPIClient.connect() as client:
            await client.get_from_test_url()

    async def main2():

        async with aiohttp.ClientSession() as session:
            client = RiotAPIClient(session=session)
            await client.get_from_test_url()


    asyncio.run(main())