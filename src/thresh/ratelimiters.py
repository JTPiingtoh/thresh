import pickle

from thresh._ratelimiters import _LeakyBucket


class LeakyBucket(_LeakyBucket):
    '''
    Implements API for Leaky Bucket, including changing rates/capacity
    '''

    def __init__(self, 
                rate = 100 / 120, 
                tolerance = 0
            ):
        
        super().__init__(rate, tolerance)

    
    def set_rate(self, rate) -> None:
        self._set_rate(rate)

    def get_rate(self):
        return self._rate

    def set_capacity(self, capacity) -> None:
        self._set_capacity(capacity)        

    def acceptable_request(self) -> bool:
        return self._acceptable_request()
    
    
