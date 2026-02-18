import aiohttp
import asyncio

from asyncio import EventLoop

from contextlib import asynccontextmanager
from typing import Final, AsyncIterator, Iterable, Generator

from thresh.ratelimiters import RiotAPIRateLimiter
from thresh.helpers import create_aiohttp_closed_event



class RiotAPIClient():

    _session: Final[aiohttp.ClientSession]
    _rate_limiter: Final[RiotAPIRateLimiter]

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._rate_limiter = RiotAPIRateLimiter()
    

    @classmethod
    @asynccontextmanager
    async def connect(cls, session: aiohttp.ClientSession | None = None) -> AsyncIterator[RiotAPIClient]:

        if session == None:
            session: aiohttp.ClientSession = aiohttp.ClientSession()
        try:
            yield cls(session) 
        finally:

            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()
            await session.close()
            


    async def handle_request(self, **kwargs):
        session = self._session
        
        response_object = []

        # request_object can either be a list of dicts with a least 1 row, or a generator, yeilding dict(s) with
        # the endpoint options
        request_object: Iterable[dict] = [{}]

        if "options" in kwargs:
            request_object = kwargs["options"]
            if not isinstance(request_object, Iterable):
                raise ValueError("options must be an iterable of dicts")
            elif isinstance(request_object, Generator):
                pass
            elif len(request_object) == 0:
                return None
            
        else:
            for argument, value in kwargs.items():
                request_object.append(dict(argument, value))

        # TODO: make this into a task group

        async with asyncio.TaskGroup() as tg:
            async with self._rate_limiter as limiter:
                middlewares = []
                middlewares.append(limiter)
                for request in request_object: 
                    async with session.get(request["url"], headers=request["options"], middlewares=middlewares) as resp:
                        tg.create_task(response_object.append(await resp.text))

        return response_object

    async def get_from_test_url(self, region, tier, options: Iterable):
        return await self.handle_request("http://127.0.0.1:5000", options)




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