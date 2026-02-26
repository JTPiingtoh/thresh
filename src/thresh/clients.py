import asyncio

from contextlib import asynccontextmanager
from typing import Final, AsyncIterator, Iterable, Generator, Callable
from functools import wraps

import aiohttp

from thresh.ratelimiters import RiotAPIRateLimiter, BaseRateLimiter
from thresh.helpers import create_aiohttp_closed_event
from thresh.middlewares import Response_object_maker_middleware


class RiotAPIClient():

    _session: Final[aiohttp.ClientSession]
    _rate_limiter: Final[BaseRateLimiter]

    def __init__(self, session: aiohttp.ClientSession, rate_limiter: BaseRateLimiter):
        self._session = session
        self._rate_limiter = rate_limiter
    

    @classmethod
    @asynccontextmanager
    async def connect(
        cls, session: aiohttp.ClientSession | None = None, 
        rate_limiter: BaseRateLimiter | None = None
        ) -> AsyncIterator["RiotAPIClient"]:

        if session == None:
            session: aiohttp.ClientSession = aiohttp.ClientSession()
        if rate_limiter == None:
            rate_limiter = RiotAPIRateLimiter()

        rate_limiter.load_state()

        try:
            yield cls(session, rate_limiter) 

        finally:
            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()
            await session.close()
            rate_limiter.save_state()
            



    async def handle_request(self, url_factory: Callable[[dict], str], **kwargs):
        
        response_object = []

        # request_object can either be a list of dicts with a least 1 row, or a generator, yeilding dict(s) with
        # the endpoint options
        request_object: Iterable[dict] = [{}]

        if "parameter_iterable" in kwargs:
            request_object = kwargs["parameter_iterable"]
            if not isinstance(request_object, Iterable):
                raise ValueError("parameter_iterable must be an iterable of dicts")
            elif isinstance(request_object, Generator):
                pass
            elif len(request_object) == 0:
                return None
            
        else:
            for argument, value in kwargs.items():
                request_object.append(dict(argument, value))

        response_maker = Response_object_maker_middleware()
        
        limiter = self._rate_limiter

        async with asyncio.TaskGroup() as tg:
            for request_parameter_dict in request_object: 
                # TODO: add api key to headers
                async with self._session.get(url=url_factory(**request_parameter_dict), middlewares=[limiter, response_maker]) as resp:
                    event: asyncio.Event = asyncio.Event()
                    tg.create_task(event.wait())
                    _ = await resp.text()
                    event.set()
                   

        return response_object

    @staticmethod
    def riot_api_endpoint(base_url: str):
        '''
        All client endpoint APIs should be decorated with this function.
        Creates a url_builder to easily create multiple requests from a given endpoint, and
        calls handle_request().
        '''
        def decorator(func):

            @wraps(func)
            async def wrapper(self, **kwargs):
                
                def url_factory(**kwargs):
                    return base_url.format(**kwargs)                    

                # url = base_url.format(**kwargs)
                # return url
                return await self.handle_request(
                    url_factory=url_factory, **kwargs
                )
            
            return wrapper
        return decorator
     

    @riot_api_endpoint("http://127.0.0.1:5000/{region}/{tier}")
    async def get_from_test_url(
            self, 
            region: str | None = None, 
            tier: str | None = None, 
            parameter_iterable: Iterable | None = None
        ):
        ...


    @riot_api_endpoint("https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}")
    async def get_league_v4_entries_queue_tier_division(
        self,
        *
        region,
        queue,
        tier,
        division,
        page,
        parameter_dict
    ):
        ...



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