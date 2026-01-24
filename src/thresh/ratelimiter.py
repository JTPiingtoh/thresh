# Global rate limiter that will be used by all RiotAPIClients

# TODO application rate limit: Global rate limiter for the API Key. All Clients need to share a single instance of this class
# TODO method rate limit: Rate limit for each API endpoint. Each endpoit get methid will need to invoke an instance of this class

# TODO clients need to know whether their API call window is is sync with the server's view


import time
from math import ceil
import requests
import pickle
from functools import cached_property


# Implements the gloabal state of the endpoints bucket using context management
class API_Key_Bucket_state():


    def _get_api_rate(self):
        response = requests.get(self._url)

        # TODO: Make this key part of a global dataclass the riot API speficically
        # TODO: current form matches local flask test server: remap to RIOT API
        requests_per, seconds = response.headers["X-App-Rate-Limit"].split(":")
        return float(requests_per) / float(seconds)


    def __enter__(self):
        self._url = "http://127.0.0.1:5000"

        # check cache for previous bucket state, compare to api rate
        try:
            with open("API_Key_Bucket_state.pkl", "rb") as file:
                self.bucket = pickle.load(file)
                if not self.bucket.accept_request():
                    # TODO: Kill process and log errors
                    raise RuntimeError("429 occured when pinging!")

                current_rate = self._get_api_rate()                
                if self.bucket.rate != current_rate:
                    self.bucket = LeakyBucket(rate=current_rate)

        except FileNotFoundError:
            self.bucket = LeakyBucket(rate=self._get_api_rate())

        return self.bucket

    def __exit__(self, *_):
        with open("API_Key_Bucket_state.pkl", "wb") as file:
            pickle.dump(self.bucket, file)

        return False

    
    
    # TODO store rate cache

    
    def _update_state(self):
        rate = self._get_api_rate()
        self._rate = rate

    

class LeakyBucket():

    """
    initiated from the global bucket state
    """
    def __init__(
        self,
        rate: str | float = 100/120,
        tolerance: int = 0
        ):

        # TODO: add checks for ints

        # if isinstance(rate, str):
        #     try:
        #         requests_per, seconds = rate.split(":")
        #         self.capacity = int(seconds) / int(requests_per)
        #     except ValueError:
        #         raise ValueError(f"Expected ratio like '100:120', got {rate}")
        # else:
        #     # TODO T aka capacity is not rate, it is a length of time
        #     self.capacity = 1 / rate

        self.rate = rate
        self.capacity = 1 / rate

        if tolerance > self.capacity:
            raise ValueError(f"tolerance must be less than capacity (T). Got tolerance: {tolerance}, capacity: {self.capacity}")

        self.tolerance = tolerance
        self.value = 0
        self.last_conforming_time = time.time()
        
        
        

    # Leaky bucket seems to only be able to handle around 563 requests per second as of v0.0.1

    def set_state(self, aux_value, arrival_time):
        self.value = max(0, aux_value) + self.capacity
        self.last_conforming_time = arrival_time

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