import aiohttp
import asyncio

from contextlib import asynccontextmanager

from typing import Final, AsyncIterator


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
            from thresh.helpers import create_aiohttp_closed_event

            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()

                    

    async def get_from_test_url(self):
        await asyncio.sleep(0)



if __name__ == "__main__":

    # BUG: causes ubclosed client session
    async def main():
        async with RiotAPIClient.connect() as client:
            # await client.get_from_test_url()
            ...

    async def main2():

        async with aiohttp.ClientSession() as session:
            client = RiotAPIClient(session=session)
            # await client.get_from_test_url()
            ...


    asyncio.run(main2())