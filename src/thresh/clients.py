import aiohttp
import asyncio

from contextlib import asynccontextmanager
from typing import Final, AsyncIterator

from thresh.ratelimiters import RiotAPILimiter

class RiotAPIClient():

    _session: Final
    _rate_limiter: Final

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._rate_limiter: RiotAPILimiter = RiotAPILimiter()
    

    @classmethod
    @asynccontextmanager
    async def connect(cls, session: aiohttp.ClientSession | None = None) -> AsyncIterator:


        if session == None:
            session: aiohttp.ClientSession = aiohttp.ClientSession()
        try:
            yield cls(session) 
        finally:
            from thresh.helpers import create_aiohttp_closed_event

            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()
            await session.close()



    async def get_from_test_url(self):

        session: aiohttp.ClientSession = self._session

        url = "http://127.0.0.1:5000"

        # response = Handler().handle()

        # self.handler(...).handle_request(...)





if __name__ == "__main__":


    # init and connect are called
    async def main():
        async with RiotAPIClient.connect() as riot_client:
            
            _ = await riot_client.get_from_test_url()
            

    # init is called
    # BUG: does not call connect()
    async def main2():
        async with aiohttp.ClientSession() as session:
            riot_client = RiotAPIClient(session=session)
            _ = await riot_client.get_from_test_url()
            


    asyncio.run(main2(), debug=True)