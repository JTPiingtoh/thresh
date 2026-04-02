import asyncio

from contextlib import asynccontextmanager
from typing import Final, AsyncIterator, Iterable, Generator, Callable
from types import FrameType
import inspect

import aiohttp

from thresh.ratelimiters import RiotAPIRateLimiter, BaseRateLimiter
from thresh.extras.aiohttp_closed_event import create_aiohttp_closed_event
from thresh._middlewares import _retry_middleware, RateLimitMiddleware
from thresh.request_object import RequestObject

class RiotAPIClient():

    _session: Final[aiohttp.ClientSession]
    _rate_limiter: Final[BaseRateLimiter]

    def __init__(self, session: aiohttp.ClientSession, rate_limiter: BaseRateLimiter, middlewares: list[Callable] | None = None):
        self._session = session
        self._rate_limiter = rate_limiter
        self._middlewares = middlewares
    

    @classmethod
    @asynccontextmanager
    async def connect(
        cls, 
        session: aiohttp.ClientSession | None = None, 
        rate_limiter: BaseRateLimiter | None = None,
        middlewares: list[Callable] | None = None
        ) -> AsyncIterator["RiotAPIClient"]:

        if session == None:
            session = aiohttp.ClientSession()
        if rate_limiter == None:
            rate_limiter = RiotAPIRateLimiter()
        

        try:
            yield cls(session, rate_limiter, middlewares) 

        finally:
            all_is_lost: asyncio.Event = create_aiohttp_closed_event(session)
            await all_is_lost.wait()
            await session.close()
  
    

    async def _build_request_object(self, base_url: str, caller_middlewares: list[Callable] | None = None) -> aiohttp.ClientResponse:


        cur_frame: FrameType | None = inspect.currentframe()
        caller_frame: FrameType | None

        if cur_frame:
            caller_frame = cur_frame.f_back
        else:
            raise RuntimeError("inspect.currentframe failed")

        if not caller_frame:
            raise RuntimeError("_build_request_object was outside of a function body.")
        caller_args = caller_frame.f_locals
        caller_name = caller_frame.f_code.co_name

        
        default_middlewares: list[Callable] = [RateLimitMiddleware(self._rate_limiter)]
        client_middlewares: list[Callable] | None = self._middlewares
        request_middlewares: list[Callable] | None

        if caller_middlewares:
            request_middlewares = caller_middlewares
        else:
            request_middlewares = client_middlewares

        if request_middlewares:
            request_middlewares += default_middlewares
        else:
            request_middlewares = default_middlewares

        request_object = RequestObject(
            base_url=base_url, 
            parameters=caller_args, 
            session=self._session,
            middlewares=request_middlewares,
            endpoint_name=caller_name
        )

        return await request_object.send_request()
        
    
        
    
    async def get_from_test_url(
            self, 
            *,
            region: str, 
            tier: str, 
            division: str,
            middlewares: list[Callable] | None = None,
        ):
        return await self._build_request_object(base_url="http://127.0.0.1:5000/{region}/{tier}/{division}", caller_middlewares=middlewares)


    async def get_league_v4_entries_queue_tier_division(
        self,
        *,
        region,
        queue,
        tier,
        division,
        page,
        middlewares
    ):
        return await self._build_request_object(base_url="https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}", caller_middlewares=middlewares)

