# feb 11 2026: Old approach for the ratelimiter, using a bucket model. Ultimately decided to go with a header only approach


import pickle
import time
import asyncio

from dataclasses import dataclass
from contextlib import contextmanager
from typing import Final, Generator
from collections import defaultdict
from abc import ABC, abstractmethod

from aiohttp import ClientRequest, ClientHandlerType, ClientResponse, ClientSession
from aiohttp.web import HTTPClientError
from multidict import CIMultiDictProxy



@dataclass
class THRESHKEYS:
    RIOT_API_RATELIMITER_KEY: Final[str]  = "Client_RiotAPI_RLimiter_1"

@dataclass
class RiotAPILimiterState:
    pass


# TODO: make threadsafe
limiter_state_cache = {}


# TODO: handle window edge
def default_index_value():
    return (0,0,0,0)


class BaseRateLimiter(ABC):
    '''
    Base class for rate limiters, stipulating that any rate limiter shall be able
    to load its own state, compute a wait for, and be able to sync itself. 
    An async __call__() method should also be defined for use as as middleware. 
    '''

    @abstractmethod
    def load_limiter(self) -> Generator["BaseRateLimiter", None, None]:
        ...

    @abstractmethod
    def load_state(self) -> None:
        ...

    @abstractmethod
    def save_state(self) -> None:
        ...

    @abstractmethod
    async def compute_wait_for(self) -> float:
        ...

    @abstractmethod
    async def sync_limiter(self, headers: CIMultiDictProxy[str]) -> None:
        ...




class RiotAPIRateLimiter(BaseRateLimiter):
    '''
    Default rate limiter for thresh, limiting requests purely by parsing response headers.
    '''


    def __init__(self):

        self.targets_to_update: list = []
        self._index = defaultdict(default_index_value)

    
    def load_state(self) -> None:

        try:
            with open("index.pkl", "rb") as f:
                self._index = pickle.load(f)
            with open("targets_to_update.pkl", "rb") as f:
                self.targets_to_update = pickle.load(f)
        except FileNotFoundError:
            pass
        except EOFError:
            pass

    
    def save_state(self) -> None:

        with open("index.pkl", "wb") as f:
            pickle.dump(self._index, f)
        with open("targets_to_update.pkl", "wb") as f:
                pickle.dump(self.targets_to_update, f)


    @contextmanager
    def load_limiter(self) -> Generator[BaseRateLimiter, None, None]:

        try:
            with open("index.pkl", "rb") as f:
                self._index = pickle.load(f)
            with open("targets_to_update.pkl") as f:
                self.targets_to_update = pickle.load(f)
        except FileNotFoundError:
            pass
        except EOFError:
            pass

        try:
            yield self
        finally:
            with open("index.pkl", "wb") as f:
                pickle.dump(self._index, f)
        

    async def compute_wait_for(self, parameters: dict) -> float:

        wait_for: float = 0
        for target in [
            ("app", 0, parameters["region"]), # TODO: add region etc
            ("app", 1, parameters["region"]),
            ("method", 0, parameters["region"]),
            ("method", 1, parameters["region"])
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
            
            scope, id, region, *others = target_key

            if id >= len(header_limits[scope]):
                self._index[scope, id, region, *others] = (0, 100, 3_600, 0)
                continue

            self._index[scope, id, region, *others] = (
                header_counts[scope][id][0],
                header_limits[scope][id][0],
                header_limits[scope][id][1] + response_time, # window expires
                response_time - request_time, # latency  
            )

        #BUG: If an error occurs in this coroutine due to the code above, this will never get called! e.g a value error where target unpacking 
        # gives the incorrect number of values.
        # The ratelimiter state is still saved during shutdown however, meaing the invalid targets also get saved, and can raise the error again!
        self.targets_to_update = []

        return
    


    


    
    
