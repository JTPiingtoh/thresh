# Global rate limiter that will be used by all RiotAPIClients

# TODO application rate limit: Global rate limiter for the API Key. All Clients need to share a single instance of this class
# TODO method rate limit: Rate limit for each API endpoint. Each endpoit get methid will need to invoke an instance of this class

# TODO clients need to know whether their API call window is is sync with the server's view


import time
from math import ceil
import requests
import redis


class Endpoint_rates():

    """
    Prototype class for check an endpoint's ratelimits, and storing it in memory. 
    """
    def __init__(self):
        self.url = "http://127.0.0.1:5000"

    def ping(self):
        response = requests.get(self.url)
        rate = 

    # TODO: factor in ping to lct


# Implements the gloabal state of the endpoints bucket
class Global_Bucket_state(Endpoint_rates):
    """

    """
    def __init__(self):
        self.url = "http://127.0.0.1:5000"




class LeakyBucket():

    """
    initiated from the global bucekt state
    """
    def __init__(
        self,
        rate: str | float = "100:120",
        tolerance: int = 0
        ):

        # TODO: add checks for ints

        if isinstance(rate, str):
            try:
                requests_per, seconds = rate.split(":")
                self.capacity = int(seconds) / int(requests_per)
            except ValueError:
                raise ValueError(f"Expected ratio like '100:120', got {rate}")
        else:
            # TODO T aka capacity is not rate, it is a length of time
            self.capacity = 1 / rate

        if tolerance > self.capacity:
            raise ValueError(f"tolerance must be less than capacity (T). Got tolerance: {tolerance}, capacity: {self.capacity}")

        self.tolerance = tolerance
        self.value = 0
        self.last_conforming_time = time.time()
        
        self._redis_instance = redis.Redis(decode_responses=True)
        self._redis_winlen_key = "thresh:LeakyBucket:1:winlen" # length of the window
        self._redis_winstart_key = "thresh:LeakyBucket:1:winlen" # start of the last window

    # Leaky bucket seems to only be able to handle around 563 requests per second as of v0.0.1

    def _set_window_start(self):
        self._redis_instance.set(self._redis_winstart_key, time.time())


    def _get_window_start(self):
        return self._redis_instance.get(self._redis_winstart_key)


    def accept_request(self):

        arrival_time = time.time()
        aux_value = self.value - (arrival_time - self.last_conforming_time) 

        # between the first and second request, this is prematurely computing to false
        if ceil(aux_value * self.capacity) / self.capacity > self.tolerance:
            return False
        else:
            self.value = max(0, aux_value) + self.capacity
            self.last_conforming_time = arrival_time
            return True




class AppRateLimiter():
    """
    Limiter used by all endpoints
    """
    ...


class MethodLimiter():
    ...

if __name__ == "__main__":
    bucky = LeakyBucket(10/12)
    print(bucky.rate)