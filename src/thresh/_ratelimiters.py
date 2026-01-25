import time
from math import ceil


class _LeakyBucket():

    """
    Base class implementing leaky bucket logic. Not intended to be interacted with directy
    """
    def __init__(
        self,
        rate: str | float = 100/120,
        tolerance: int = 0
        ):

        self._rate = rate
        self._capacity = 1 / rate

        if tolerance > self._capacity:
            raise ValueError(f"tolerance must be less than capacity (T). Got tolerance: {tolerance}, capacity: {self.capacity}")

        self._tolerance = tolerance
        self._value = 0
        self._last_conforming_time = time.time()
              
    
    def _set_rate(self, rate):
        self._rate = rate
        self._capacity = 1 / rate


    def _set_capacity(self, capacity):
        self._capacity = capacity
        self._rate = 1 / capacity
        

    def _acceptable_request(self):

        arrival_time = time.time()
        aux_value = self._value - (arrival_time - self._last_conforming_time) 

        # between the first and second request, this is prematurely computing to false
        if ceil(aux_value * self._capacity) / self._capacity > self._tolerance:
            return False
        else:
            self._value = max(0, aux_value) + self._capacity
            self._last_conforming_time = arrival_time
            return True