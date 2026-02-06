import pickle
import time
import asyncio
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Final
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse

@dataclass
class THRESHKEYS:
    RIOT_API_RATELIMITER_KEY: Final[str]  = "Client_RiotAPI_RLimiter_1"

@dataclass
class RiotAPILimiterState:
    pass


# TODO: make threadsafe
limiter_state_cache = {}


class RiotAPILimiter():
    def __init__(self):
        self._seconds_per_request: float = 0
        self._last_conforming_time: float = 0.0
        self._window_size: int = 0
        self._window_count: int = 0
        self._invoked = False


    @contextmanager
    def invoke_limiter(self):
        self._invoked = True
        self._load_and_set_state()
        try:
            yield self
        finally:
            self._invoked = False
            self._save_state()


    def _set_state(self, limit_counts: str, rate_limits: str) -> None:
        
        # find slowest rate
        rates: list[float] = []
        window_sizes: list[float] = []
        for rate_limit in rate_limits.split(","):
            requests, per_second = rate_limit.split(":")
            rates.append(float(requests) / float(per_second))
            # keep window sizes as an int
            window_sizes.append(int(per_second))

        slowest_rate: float = min(rates)
        self._seconds_per_request = 1.0 / slowest_rate
        # set window size and count according to slowest rate
        slowest_rate_index: int = rates.index(slowest_rate)
        self._window_size = window_sizes[slowest_rate_index]
        self._window_count: int = limit_counts.split(",")[slowest_rate_index][0]


    def _save_state(self) -> None:

        def create_state():
            save = RiotAPILimiterState()
            for name, value in self.__dict__.items():
                setattr(save, name, value)
            return save

        limiter_state_cache[THRESHKEYS.RIOT_API_RATELIMITER_KEY] = create_state()
    

    def _load_and_set_state(self) -> None:

        try:
            load: RiotAPILimiterState = limiter_state_cache[THRESHKEYS.RIOT_API_RATELIMITER_KEY]
            for name, value in load.__dict__.items():
                setattr(self, name, value)

        except KeyError:
            # will defer to __init__() values
            pass

        
    async def _acceptable_request(self):
        '''
        Delays execution until request is within rate limit.

        :param self: 
        '''
        if not self._invoked:
            raise RuntimeError("Rate limiter can only test requests once")
        time_since_last_sent = time.time() - self._last_conforming_time
        
        # if interval is greater than capacity, wait, then send request
        if time_since_last_sent < self._seconds_per_request:
            await asyncio.sleep(self._seconds_per_request - time_since_last_sent)
        self._last_conforming_time = time.time()

        return True
    
    
    async def __call__(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        await self._acceptable_request()
        resp = await handler(req)
        # set the state of the limiter based on the response headers.

        return resp

    


    
    
