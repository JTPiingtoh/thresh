import pickle
import time
import asyncio



class RiotAPILimiter():
    def __init__(
    self,
    rate: str | float = 100/120,
    ):

        self._rate = rate
        self._seconds_per_request = 1 / rate
        self._last_conforming_time = 0.0


    async def acceptable_request(self):
        time_since_last_sent = time.time() - self._last_conforming_time
        
        # if interval is greater than capacity, wait, then send request
        if time_since_last_sent < self._seconds_per_request:
            await asyncio.sleep(self._seconds_per_request - time_since_last_sent)
        self._last_conforming_time = time.time()

        return True
    
    # will tell the client how long to wait, given the context of the request
    async def wait_for(self, ratelimit_middleware):
        ...



    
    
