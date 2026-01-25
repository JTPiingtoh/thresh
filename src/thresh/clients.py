import requests
import pickle
from dataclasses import dataclass
from http import HTTPStatus

HTTPStatus.TOO_MANY_REQUESTS

from thresh.ratelimiters import LeakyBucket
from thresh._datastructures import RingBuffer

_DEFAULT_RATE = 100/120

@dataclass
class ClientRateLimiterKeys:
    LEAKYBUCKET = "Client_LBucket_1.pkl"


class RiotAPIClient():
    '''
        Handles the use of a ratelimiter, updating and saving its state as needed, and will call transformers, piplines etc
    '''

    def __enter__(self):

        # check cache for previous bucket state, compare to api rate
        # TODO: replace pickle with in-house caching
        try:
            with open(ClientRateLimiterKeys.LEAKYBUCKET, "rb") as file:
                self.rate_limiter = pickle.load(file)

        except FileNotFoundError:
            self.rate_limiter = LeakyBucket(rate=_DEFAULT_RATE, tolerance=0)


        self.buffer = RingBuffer
        self.pipeline = ...

        return self
        

    # TODO: make this into a async generator object?
    def get_data_from_test_api(self, dummy_option):
        URL = "http://127.0.0.1:5000"

        urls = [URL for _ in range(n_requests)]

        # TODO: add 
        for urls in urls:
            if not self.rate_limiter.acceptable_request():
                continue
            
            response = requests.get(URL)
            response.raise_for_status()

            requests_per, seconds = response.headers["X-App-Rate-Limit"].split(":")
            rate = float(requests_per) / float(seconds)

            if self.rate_limiter.get_rate() != rate:
                self.rate_limiter.set_rate(rate)

            yield response

    
    def __exit__(self, exc_type, exc_value, traceback):
        with open(ClientRateLimiterKeys.LEAKYBUCKET, "wb") as file:
            pickle.dump(self.rate_limiter, file)
        return False




    # async def get_league_matches_exp_v4_by_queue_tier_division(
    #         self,
    #         region,
    #         page,
    #         queue,
    #         tier,
    #         division
    #         ):
    #     return await self.get(f"https://{region}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}")