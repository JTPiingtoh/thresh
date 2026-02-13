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
        self.targets_to_update: list = []


    async def compute_wait_for(self) -> float:

        wait_for: float = 0
        self.sync = ...
        # self.pinging_targets

        return wait_for
    

    async def sync_limiter(self, headers, request_time: float, response_time: float) -> None:

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
        # If the number of targets is greater than the number of rate_limits present in the headers, we have effectively lost information about that 
        # rate limit. we should set it to a suitable conservative value and with a long window

        for scope, id, *others in self.targets_to_update:

            if id >= len(header_limits):
                self._index(scope, id, *others) = (0,100,3_600,0)
                continue

            self._index[scope, id, *others] = (
                header_limits[scope][id][0],
                header_counts[scope][id][0],
                header_limits[scope][id][1] + response_time,
                response_time - request_time
            )


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

    


    
    
