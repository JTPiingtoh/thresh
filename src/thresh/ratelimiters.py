# feb 11 2026: Old approach for the ratelimiter, using a bucket model. Ultimately decided to go with a header only approach


import pickle
import time
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import Final
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from aiohttp.web import HTTPClientError

@dataclass
class THRESHKEYS:
    RIOT_API_RATELIMITER_KEY: Final[str]  = "Client_RiotAPI_RLimiter_1"

@dataclass
class RiotAPILimiterState:
    pass


# TODO: make threadsafe
limiter_state_cache = {}


# TODO: handle window edge

class RiotAPIBucketLimiter():
    def __init__(self):
        
        self.sync: bool = False
        self._index = ...


    async def compute_wait_for(self) -> float:

        wait_for: float = 0
        self.sync = ...

        return wait_for
    

    async def sync_limiter(self, headers, request_time: float, response_time: float) -> None:

        # dict[
        # tuple(scope, id, etc), limit, count, expires
        # ]

        # [app, 0, ...] = limit, count, expries

        header_limits = {
            "app": [limit for limit, _ in rate_limit.split(":") for rate_limit in headers.get("X-App-Rate-Limit").split(",")],
            "method": ...
        }

        return
    

    async def measure_request(
            self, req: ClientRequest, handler: ClientHandlerType
        ) -> tuple[ClientResponse, float, float]:

        request_time: float = time.time()
        resp = handler(req)
        response_time: float = time.time()

        return (resp, request_time, response_time)


    # TODO: add logic that will force a wait if count reaches limit for a given window
    async def __call__(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        
         
        while True:
            wait_for = await self.compute_wait_for()
            if wait_for <= 0:
                break
        
        resp: ClientResponse 
        
        if self.sync:
            # call if computer_wait_for() finds headers that need to be updated
            request_time: float 
            response_time: float
            resp, request_time, response_time = await self.measure_request(handler, req)
            self.sync_limiter(resp.headers, request_time, response_time)
        else:
            resp = await handler(req)


        return resp

    


    
    
