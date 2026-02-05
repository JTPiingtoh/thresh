import pickle
import time
import asyncio
from dataclasses import dataclass

@dataclass
class ClientRateLimiterKeys:
    RIOT_API_RATELIMITER_KEY = "Client_RiotAPI_RLimiter_1.pkl"

class RiotAPILimiter():
    def __init__(
    self,
    requests: int = 100,
    window_size: int = 120
    ):

        self._seconds_per_request: float = 1 / ( float(requests) / float(window_size) )
        self._last_conforming_time: float = 0.0
        self._window_size: int = window_size
        self._window_count: int = 0


    def set_state(self, limit_counts: str, rate_limits: str):
        
        # find slowest rate
        rates: list[float] = []
        window_sizes: list[float] = []
        for rate_limit in rate_limits.split(","):
            requests, per_second = rate_limit.split(":")
            rates.append(float(requests / float(per_second)))
            # keep window sizes as an int
            window_sizes.append(int(per_second))

        slowest_rate: float = min(rates)
        self._seconds_per_request = 1.0 / slowest_rate
        # set window size and count according to slowest rate
        slowest_rate_index: int = rates.index(slowest_rate)
        self._window_size = window_sizes[slowest_rate_index]
        self._window_count: int = limit_counts.split(",")[slowest_rate_index][0]

    async def request_accepted(self):
        '''
        Delays execution until request is within rate limit.

        :param self: 
        '''
        time_since_last_sent = time.time() - self._last_conforming_time
        
        # if interval is greater than capacity, wait, then send request
        if time_since_last_sent < self._seconds_per_request:
            await asyncio.sleep(self._seconds_per_request - time_since_last_sent)
        self._last_conforming_time = time.time()

        return True
    
    # will tell the client how long to wait, given the context of the request
    async def wait_for(self, ratelimit_middleware):
        ...

    


    
    
