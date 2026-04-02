import time

from dataclasses import dataclass
from collections import defaultdict
from abc import ABC, abstractmethod
from multidict import CIMultiDictProxy
from typing import Literal, List

from thresh.request_object import RequestObject

class WaitFlags():
    CONFORMING = -1.0
    SYNC = -2.0
    @staticmethod
    def conforming(wait_for: float):
        return wait_for == WaitFlags.CONFORMING

    @staticmethod
    def sync_required(wait_for: float):
        return wait_for == WaitFlags.SYNC
        


# TODO: add error logging
# TODO: add mechanism for removing stale targets
class BaseRateLimiter(ABC):
    '''
    Base class for rate limiters, stipulating that any rate limiter shall be able
    to load its own state, compute a wait for, and be able to sync itself. 
    Use SYNC_FLAG to indicate whether syncing is required for that request.
    '''

    @abstractmethod
    async def compute_wait_for(self, request_object: RequestObject) -> float:
        ...

    @abstractmethod
    async def sync(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:
        ...



class RiotAPIRateLimiter(BaseRateLimiter):
    '''
    Default rate limiter for thresh, limiting requests purely by parsing response headers.
    '''
    @staticmethod
    def default_index_value() -> tuple[int, int, float, float, float]:
        '''
        default count, limit, window_expire, latency, pinged
        '''
        return (0,0,0,0,0)

    def __init__(self):
        self.targets_to_update: dict[tuple[Literal['app', 'method'], int, str], float] = {}
        self._index = defaultdict(RiotAPIRateLimiter.default_index_value)
        self._base_targets: list[tuple[Literal['app', 'method'], int]] = [
            ("app", 0),  
            ("app", 1), 
            ("method", 0),
            ("method", 1)
        ]
    
        

    # TODO: add error logging
    # TODO: add mechanism for removing stale targets

    async def compute_wait_for(self, request_object: RequestObject) -> float:

        pinging_targets = []
        requesting_targets = []
        request_time = time.time()
        wait_for: float = 0

        for base_target in self._base_targets:

            target = *base_target, request_object.region
            count, limit, window_expire, latency, pinged = self._index[target]

            
            # pinging means we don't yet know this window's state
            pinging = pinged and request_time - pinged < 10

            if pinging:
                wait_for = max(wait_for, 0.1)
            # will always be true in uninitited index
            elif request_time > window_expire:
                pinging_targets.append(target)
            elif count >= limit or request_time > window_expire - latency:
                wait_for = max(wait_for, window_expire - request_time)
            else:
                requesting_targets.append(target)

        if wait_for <= 0:

            if not pinging_targets:
                wait_for = WaitFlags.CONFORMING
            else :
                for pinging_target in pinging_targets:
                    self.targets_to_update[pinging_target] = request_time 
                    self._index[pinging_target] = (0, 0, 0, 0.0, time.time()) 
                wait_for = WaitFlags.SYNC
            for r_target in requesting_targets:
                count, limit, window_expire, latency, pinged = self._index[r_target]
                self._index[r_target] = (count + 1, limit, window_expire, latency, pinged)        


            # if all targets complied, update. If a wait_for has been used,
            # count does not increase                
        return wait_for
    
    # TODO: Fix for type checker
    async def sync(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:    

        header_limits: dict[Literal["app", "method"], List[List[int]]]
        header_counts: dict[Literal["app", "method"], List[List[int]]]

        def get_header(key: str) -> str:
            value: str | None = headers.get(key)
            if not value:
                raise RuntimeError(f"Key {key} not found in response headers.")
            return value


        header_limits = {
            "app": [[int(v) for v in rate_limit.split(":")] for rate_limit in get_header("X-App-Rate-Limit").split(",")],
            "method": [[int(v) for v in rate_limit.split(":")] for rate_limit in get_header("X-Method-Rate-Limit").split(",")]
        }

        header_counts = {
            "app": [[int(v) for v in rate_limit.split(":")] for rate_limit in get_header("X-App-Rate-Limit-Count").split(",")],
            "method": [[int(v) for v in rate_limit.split(":")] for rate_limit in get_header("X-Method-Rate-Limit-Count").split(",")]
        }
        
        if len(header_limits) != len(header_counts):
            raise RuntimeError("Limit and counts headers are not of equal length")

        # targets need to be updated when window is reached, or timeout has occured.
        # expires will be when we can send the final request for that window. Therefor it must assume
        # the window started as early as possible, ie the request_time/lower bound
        # If the number of targets is greater than the number of rate_limits present in the headers, there
        # we don't have info re that ratelimit, we need to give it a stasis like state 

        response_time = time.time()

        # TODO: change targets to update to some other data structure: list is resulting excessively long 
        # targets_to_update

        for base_target in self._base_targets:
            region: str = request_object.region
            target: tuple[Literal['app', 'method'], int, str] = *base_target, region
            try:
                request_time: float = self.targets_to_update[target]
            except KeyError:
                continue

            scope, id, *others = target
            if id >= len(header_limits[scope]):
                self._index[scope, id,  *others] = (0, 100, 3_600, 0, 0)
                continue

            self._index[scope, id, *others] = (
                header_counts[scope][id][0],
                header_limits[scope][id][0],
                header_limits[scope][id][1] + response_time, # window expires
                response_time - request_time, # latency  
                0.0
            )

        self.targets_to_update = {}
        

        #BUG: If an error occurs in this coroutine due to the code above, this will never get called! e.g a value error where target unpacking 
        # gives the incorrect number of values.
        # The ratelimiter state is still saved during shutdown however, meaing the invalid targets also get saved, and can raise the error again!

        return
    


    


    
    
