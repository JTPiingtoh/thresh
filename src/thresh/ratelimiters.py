# feb 11 2026: Old approach for the ratelimiter, using a bucket model. Ultimately decided to go with a header only approach


import pickle
import time
import asyncio

from dataclasses import dataclass
from contextlib import contextmanager
from typing import Final, Generator
from collections import defaultdict
from abc import ABC, abstractmethod

from multidict import CIMultiDictProxy


@dataclass
class THRESHKEYS:
    RIOT_API_RATELIMITER_KEY: Final[str]  = "Client_RiotAPI_RLimiter_1"

@dataclass
class RiotAPILimiterState:
    pass


# TODO: make threadsafe
limiter_state_cache = {}




# TODO: add error logging
# TODO: add mechanism for removing stale targets
class BaseRateLimiter(ABC):
    '''
    Base class for rate limiters, stipulating that any rate limiter shall be able
    to load its own state, compute a wait for, and be able to sync itself. 
    Use SYNC_FLAG to indicate whether syncing is required for that request.
    '''

    @abstractmethod
    async def compute_wait_for(self, parameters: dict) -> float:
        ...

    @abstractmethod
    async def sync(self, wait_for: float, parameters: dict) -> None:
        ...

    @property
    @staticmethod
    def SYNC_FLAG():
        '''
        Flag response for syncing
        '''
        return -1



class RiotAPIRateLimiter(BaseRateLimiter):
    '''
    Default rate limiter for thresh, limiting requests purely by parsing response headers.
    '''
    def default_index_value():
        return (0,0,0,0,0)

    def __init__(self):
        self.targets_to_update: dict = {}
        self._index = defaultdict(RiotAPIRateLimiter.default_index_value)
        self._base_targets = [
            ("app", 0),  
            ("app", 1), 
            ("method", 0),
            ("method", 1)
        ]
    
    
        

    # TODO: add error logging
    # TODO: add mechanism for removing stale targets

    async def compute_wait_for(self, parameters: dict) -> float:

        pinging_targets = []
        requesting_targets = []
        request_time = time.time()
        wait_for: float = 0
        # for target in [
        #     ("app", 0, request_object.parameters["region"]), # TODO: add region etc
        #     ("app", 1, request_object.parameters["region"]),
        #     ("method", 0, request_object.parameters["region"]),
        #     ("method", 1, request_object.parameters["region"])
        # ]:

        for base_target in self._base_targets:

            target = *base_target, parameters["region"]
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
            if pinging_targets:
                for pinging_target in pinging_targets:
                    self.targets_to_update[pinging_target] = request_time 
                    self._index[pinging_target] = (0, 0, 0, 0, time.time()) 
                wait_for = self.SYNC_FLAG
            for r_target in requesting_targets:
                count, *values = self._index[r_target]
                self._index[r_target] = (count + 1, *values)        


            # if all targets complied, update. If a wait_for has been used,
            # count does not increase                
        return wait_for
    

    async def sync(self, wait_for: float, parameters: dict, headers) -> None:
    
        # dict[
        # tuple(scope, id, etc) : tuple(limit, count, upper_bound, latency)
        # ]

        # [app, 0, ...] = limit, count, upper_bound
        if wait_for != self.SYNC_FLAG:
            return
        
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

        # TODO: change targets to update to some other data structure: list is resulting excessively long 
        # targets_to_update

        for base_target in self._base_targets:
            
            target = *base_target, parameters["region"]
            try:
                request_time = self.targets_to_update[target]
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
                0
            )

        self.targets_to_update = {}
        

        #BUG: If an error occurs in this coroutine due to the code above, this will never get called! e.g a value error where target unpacking 
        # gives the incorrect number of values.
        # The ratelimiter state is still saved during shutdown however, meaing the invalid targets also get saved, and can raise the error again!

        return
    


    


    
    
