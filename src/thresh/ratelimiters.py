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

class RiotAPILimiter():
    def __init__(self):
        self._seconds_per_request: float = 0.0
        self._window_size: int = 0
        self._last_conforming_time: float = 0.0
        self._window_count: int = 0
        self._invoked: bool = False


    @asynccontextmanager
    async def invoke(self):
        self._invoked = True
        self._load_and_set_state()
        try:
            yield self
        finally:
            # self._invoked = False
            await self._save_state()

    
    def _set_state(self, limit_counts: str, rate_limits: str) -> None:
        
        # sort by lowest rate
        limits_counts = list(zip(rate_limits, limit_counts))

        def get_rate(_limit_count):
            requests, per_second = _limit_count[0].split(":")
            return float(requests) / float(per_second)

        slowest_rate_limit, slowest_rate_count = sorted(limits_counts, key = get_rate)[0]

        if slowest_rate_limit.split(":")[1] != slowest_rate_count.split(":")[1]:
            raise RuntimeError("ratelimit window does not equal rate limit count window.")

        slowest_requests, slowest_per_seconds = slowest_rate_limit.split(":")

        self._seconds_per_request = 1.0 / (float(slowest_requests) / float(slowest_per_seconds))
        # set window size and count according to slowest rate
        self._window_size = int(slowest_rate_count.split(":")[1])
        self._window_count = int(slowest_rate_count.split(":")[0])




        def create_state():
            save = RiotAPILimiterState()
            for name, value in self.__dict__.items():
                setattr(save, name, value)

            return save

        limiter_state_cache[THRESHKEYS.RIOT_API_RATELIMITER_KEY] = create_state()

        return
    

    def _load_and_set_state(self) -> None:

        try:
            load: RiotAPILimiterState = limiter_state_cache[THRESHKEYS.RIOT_API_RATELIMITER_KEY]
            for name, value in load.__dict__.items():
                setattr(self, name, value)

        except KeyError:
            # will defer to __init__() values
            pass

    # TODO: add logic to check the number of requests remaining. If max requests reached at the window
    # wait until start of next window
    # TODO: add saftey around clock sync 
    async def _acceptable_request(self):
        '''
        Delays execution until request is within rate limit.

        :param self: 
        '''
        if not self._invoked:
            raise RuntimeError("Rate limiter can only test requests once invoked")
        time_since_last_sent = time.time() - self._last_conforming_time
        
        # if interval is greater than capacity, wait, then send request
        if time_since_last_sent < self._seconds_per_request:
            await asyncio.sleep(self._seconds_per_request - time_since_last_sent)
        self._last_conforming_time = time.time()

        return

    
    async def __call__(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        
        await self._acceptable_request()
        resp = await handler(req)
        if resp.status == 429:
            raise RuntimeError("429")
            

        # set the state of the limiter based on the response headers.
        X_App_Rate_Limit_Count: str | None = resp.headers.get("X-App-Rate-Limit-Count")
        X_App_Rate_Limit: str | None = resp.headers.get("X-App-Rate-Limit")
        
        if X_App_Rate_Limit and X_App_Rate_Limit_Count:
            self._set_state(X_App_Rate_Limit_Count, X_App_Rate_Limit)
        else:
            # TODO: How should such an error change the state of the class instance?
            raise RuntimeError(f"Recieved no ratelimit headers from API: {X_App_Rate_Limit_Count, X_App_Rate_Limit}")


        return resp

    


    
    
