import time

from dataclasses import dataclass
from collections import defaultdict
from abc import ABC, abstractmethod
from multidict import CIMultiDictProxy
from typing import Literal, List

from thresh.request_object import RequestObject
from thresh.typing import *


class RateLimitDecision():
    '''
    Class representing the compliancy of a request
    '''
    def __init__(self, retry_after: float):
        self._retry_after: float = retry_after
        self._should_sync: bool = False

    def set_should_sync(self, b: bool):
        self._should_sync = b

    def update_retry_after(self, new_retry_after: float):
        '''
        If the new_retry_after is greater than the RateLimitDecision's current retry_after,
        RateLimitDecision().retry_after == new_retry_after
        '''
        self._retry_after = max(self._retry_after, new_retry_after)

    @property
    def is_compliant(self) -> bool:
        return self._retry_after <= 0
    
    @property
    def should_sync(self) -> bool:
        return self._should_sync
    
    @property
    def retry_after(self) -> float:
        return self.retry_after



# TODO: add error logging
# TODO: add mechanism for removing stale targets
class BaseRateLimiter(ABC):
    '''
    Base class for rate limiters, stipulating that any rate limiter shall be able
    to load its own state, compute a wait for, and be able to sync itself. 
    Use SYNC_FLAG to indicate whether syncing is required for that request.
    '''

    @abstractmethod
    async def test_compliancy(self, request_object: RequestObject) -> RateLimitDecision:
        ...

    @abstractmethod
    async def sync(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:
        ...

    async def handle_exceeded(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:
        ...




class RiotAPIRateLimiter(BaseRateLimiter):
    '''
    Default rate limiter for thresh, limiting requests purely by parsing response headers.
    '''
    @staticmethod
    def default_target_state() -> TargetState:
        return (0,0,0,0,0)

    def __init__(self) -> None:
        self.targets_to_update: dict[Target, float] = {}
        self._index : dict[Target, TargetState] = defaultdict(RiotAPIRateLimiter.default_target_state)
        self._base_targets: list[tuple[Scope, Id]] = [
            ("app", 0),  
            ("app", 1), 
            ("method", 0),
            ("method", 1)
        ]
    
        

    # TODO: add error logging
    # TODO: add mechanism for removing stale targets

    async def test_compliancy(self, request_object: RequestObject) -> RateLimitDecision:

        pinging_targets: list[Target] = []
        requesting_targets: list[Target] = []
        request_time = time.time()
        decision = RateLimitDecision(retry_after=0)
        wait_for: float = 0

        for base_target in self._base_targets:

            target = *base_target, request_object.region
            count, limit, window_expire, latency, pinged = self._index[target]

            # pinging means we don't yet know this window's state
            pinging = pinged and request_time - pinged < 10

            if pinging:
                decision.update_retry_after(0.1)
            elif request_time > window_expire:
                pinging_targets.append(target)
 
            elif count >= limit or request_time > window_expire - latency:
                decision.update_retry_after(window_expire - request_time)
            else:
                requesting_targets.append(target)

        if decision.is_compliant:

            if pinging_targets:
                for pinging_target in pinging_targets:
                    self.targets_to_update[pinging_target] = request_time 
                    self._index[pinging_target] = (0, 0, 0, 0.0, time.time()) 
                decision.set_should_sync(True)
            for r_target in requesting_targets:
                count, limit, window_expire, latency, pinged = self._index[r_target]
                self._index[r_target] = (count + 1, limit, window_expire, latency, pinged)        

        return decision
    
    async def sync(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:    

        header_limits: dict[Scope, List[List[int]]]
        header_counts: dict[Scope, List[List[int]]]

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
        # If the number of targets is greater than the number of rate_limits present in the headers, then
        # we don't have info re that ratelimit, we need to give it a stasis like state 

        response_time = time.time()

        # TODO: change targets to update to some other data structure: list is resulting excessively long 
        # targets_to_update

        for base_target in self._base_targets:
            region: Region = request_object.region
            target: Target = *base_target, region
            try:
                request_time: float = self.targets_to_update[target]
            except KeyError:
                continue

            scope, id, *others = target
            if id >= len(header_limits[scope]):
                # TODO: Does this makes sense with nascency?
                self._index[target] = (0, 100, 3_600, 0, 0)
                continue

            self._index[target] = (
                header_counts[scope][id][0],
                header_limits[scope][id][0],
                header_limits[scope][id][1] + response_time, # window expires
                response_time - request_time, # latency  
                0.0
            )

        self.targets_to_update = {}
        

    async def handle_exceeded(self, request_object: RequestObject, headers: CIMultiDictProxy[str]) -> None:
        '''
        Set all targets window_expire based on the retry_after supplied in header. 
        '''
        _retry_after: str | None = headers.get("Rety-After")

        if not _retry_after:
            raise RuntimeError("Failed to find retry-after from 429 response header")

        retry_after: float = float(_retry_after)
        now: float = time.time()

        for base_target in self._base_targets:

            target = *base_target, request_object.region
            _, limit, *_ = self._index[target]
            # count = limit just to be safe ;)
            self._index[target] = (limit, limit, now + retry_after, 0, 0)   

        return
    


    


    
    
