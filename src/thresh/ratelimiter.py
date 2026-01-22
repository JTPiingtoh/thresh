# Global rate limiter that will be used by all RiotAPIClients

# TODO application rate limit: Global rate limiter for the API Key. All Clients need to share a single instance of this class
# TODO method rate limit: Rate limit for each API endpoint. Each endpoit get methid will need to invoke an instance of this class
# TODO clients need to know whether their API call window is is sync with the server's view
# TODO need to account in sync differences between client and server

import time

from math import floor

class LeakyBucket():

    """"""
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


    def accept_request(self):

        arrival_time = time.time()
        aux_value = self.value - (arrival_time - self.last_conforming_time)

        # between the first and second request, this is prematurely computing to false
        if aux_value > self.tolerance:
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