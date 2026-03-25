import asyncio

from contextlib import asynccontextmanager
from typing import Final, AsyncIterator, Iterable, Generator, Callable
from functools import wraps
import inspect

import aiohttp

from thresh.ratelimiters import RiotAPIRateLimiter, BaseRateLimiter
from thresh.extras.aiohttp_closed_event import create_aiohttp_closed_event
from thresh.middlewares import construct_rate_limit_middleware
from thresh.request_object import RequestObject
from thresh.middlewares import request_rate_limit_middleware

class RiotAPIClient():

    _session: Final[aiohttp.ClientSession]
    _rate_limiter: Final[BaseRateLimiter]

    def __init__(self, session: aiohttp.ClientSession, rate_limiter: BaseRateLimiter):
        self._session = session
        self._rate_limiter = rate_limiter
        self.default_middlewares = [request_rate_limit_middleware] # TODO: add other middlewares
    

    @classmethod
    @asynccontextmanager
    async def connect(
        cls, 
        session: aiohttp.ClientSession | None = None, 
        rate_limiter: BaseRateLimiter | None = None
        ) -> AsyncIterator["RiotAPIClient"]:

        if session == None:
            session: aiohttp.ClientSession = aiohttp.ClientSession()
        if rate_limiter == None:
            rate_limiter = RiotAPIRateLimiter()

        try:
            yield cls(session, rate_limiter) 

        finally:
            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()
            await session.close()
  


    #TODO: remove this 
    @staticmethod
    def riot_api_endpoint(base_url: str):
        '''
        All client endpoint APIs should be decorated with this function.
        Creates a request_factory to easily create multiple requests for a given endpoint, and
        calls handle_request().
        '''
        def decorator(func):
            @wraps(func)
            async def wrapper(self: RiotAPIClient, **kwargs):
                #TODO: add middlewares
                request_object: RequestObject = RequestObject(kwargs, base_url, self._session, self._rate_limiter) 
                response: aiohttp.ClientResponse = await request_object.handle_request()
                
                return response            
            return wrapper
        return decorator
    

    async def build_request_object(self, base_url: str) -> aiohttp.ClientResponse:

        caller_frame = inspect.currentframe().f_back
        caller_args = caller_frame.f_locals
        caller_name = caller_frame.f_code.co_name
        url: Final[str]
    

        request_object = RequestObject(
            base_url=url, 
            parameters=caller_args, 
            session=self._session,
            endpoint_name=caller_name
        )

        return await request_object.send_request()
        
        
        


    # @riot_api_endpoint("http://127.0.0.1:5000/{region}/{tier}/{division}")
    
    async def get_from_test_url(
            self, 
            *,
            region: str | None = None, 
            tier: str | None = None, 
            division: str | None = None, 
        ):

        return self.build_request_object(base_url="http://127.0.0.1:5000/{region}/{tier}/{division}")


    @riot_api_endpoint("https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}")
    async def get_league_v4_entries_queue_tier_division(
        self,
        *,
        region,
        queue,
        tier,
        division,
        page,
    ):
        ...

