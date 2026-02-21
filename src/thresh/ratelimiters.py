# feb 11 2026: Old approach for the ratelimiter, using a bucket model. Ultimately decided to go with a header only approach


import pickle
import time
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import Final
from collections import defaultdict

from aiohttp import ClientRequest, ClientHandlerType, ClientResponse, ClientSession
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

class RiotAPIRateLimiter():

    _index = defaultdict(lambda:(0,0,0,0))

    def __init__(self):
        
        self.targets_to_update: list = []


    async def compute_wait_for(self) -> float:

        wait_for: float = 0
        self.sync = ...
        
        for target in [
            ("app", 0), # TODO: add region etc
            ("app", 1),
            ("method", 0),
            ("method", 1)
        ]:
            count, limit, window_expire, latency = self._index[target]

            request_time = time.time()

            if count >= limit or request_time > window_expire - latency:
                wait_for = max(wait_for, window_expire - request_time)

            if wait_for <= 0:
                self.targets_to_update.append( (target, request_time) )
                
        return wait_for
    

    async def sync_limiter(self, headers) -> None:

        # dict[
        # tuple(scope, id, etc) : tuple(limit, count, upper_bound, latency)
        # ]

        # [app, 0, ...] = limit, count, upper_bound

        header_limits = {
            "app": [[int(v) for v in rate_limit.split(":")] for rate_limit in headers.get("X-App-Rate-Limit").split(",")],
            "method": [[int(v) for v in rate_limit.split(":")] for rate_limit in headers.get("X-Method-Rate-Limit").split(",")]
        }

        header_counts = {
            "app": [[int(v) for v in rate_limit.split(":")] for rate_limit in headers.get("X-App-Rate-Limit-Count").split(",")],
            "method": [[int(v) for v in rate_limit.split(":")] for rate_limit in headers.get("X-Method-Rate-Limit-Count").split(",")]
        }

        if len(header_limits) != len(header_counts):
            raise RuntimeError("Limit and counts headers are not of equal length")

        # targets need to be updated when window is reached, or timeout has occured.
        # expires will be when we can send the final request for that window. Therefor it must assume
        # the window started as early as possible, ie the request_time/lower bound
        # If the number of targets is greater than the number of rate_limits present in the headers, there
        # we don't have info re that ratelimit, we need to give it a stasis like state 

        response_time = time.time()

        for target_key, request_time in self.targets_to_update:
            scope, id, *others = target_key

            if id >= len(header_limits[scope]):
                self._index[scope, id, *others] = (0, 100, 3_600, 0)
                continue

            self._index[scope, id, *others] = (
                header_counts[scope][id][0],
                header_limits[scope][id][0],
                header_limits[scope][id][1] + response_time, # window expires
                response_time - request_time, # latency  
            )

        self.targets_to_update = []

        return
    

    @asynccontextmanager
    def limit_session(self, session: ClientSession, middlewares: list):
        middlewares.append(self)
        self.midd
        self.session = session
        try:
            yield(self)
        finally:
            # save state here
            ...




    # TODO: add logic that will force a wait if count reaches limit for a given window
    async def __call__(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
         
        while True:
            wait_for = await self.compute_wait_for()
            if wait_for <= 0:
                break
        
        resp: ClientResponse = await handler(req)
        
        print(resp.headers)
        if self.targets_to_update:
            # call if computer_wait_for() finds headers that need to be updated
            await self.sync_limiter(resp.headers)

        return resp

    


    
    
