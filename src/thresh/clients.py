import requests
from requests.exceptions import HTTPError
import pickle
from dataclasses import dataclass
from http import HTTPStatus
import aiohttp

HTTPStatus.TOO_MANY_REQUESTS

from thresh.ratelimiters import RiotAPILimiter

_DEFAULT_RATE = 100/120

@dataclass
class ClientRateLimiterKeys:
    RIOT_API_RATELIMITER_KEY = "Client_RiotAPI_RLimiter_1.pkl"


class RiotAPIClient():
    '''
        Handles the use of a ratelimiter, updating and saving its state as needed, and will call transformers, piplines etc
    '''

    def __enter__(self):

        # check pickle cache for previous bucket state, compare to api rate
        # TODO: replace pickle with in-house caching
        try:
            with open(ClientRateLimiterKeys.LEAKYBUCKET, "rb") as file:
                self.rate_limiter = pickle.load(file)

        except FileNotFoundError:
            self.rate_limiter = RiotAPILimiter(rate=_DEFAULT_RATE)

        self.pipeline = ...

        return self
        

    # TODO: either needs to take a single option, or a list of options
    # If a list, create a task group and return the data in a suitable data
    # structure
    async def get_data_from_test_api(self, dummy_option):

        URL = "http://127.0.0.1:5000"
    
        await self.rate_limiter.acceptable_request()
        
        try:
            response = requests.get(URL)
            response.raise_for_status()

            requests_per, seconds = response.headers["X-App-Rate-Limit"].split(":")
            rate = float(requests_per) / float(seconds)

            # assumes that the window has not changed
            if self.rate_limiter.get_rate() != rate:
                self.rate_limiter.set_rate(rate)

        except HTTPError as e:
            print(f"HTTPError: {e}")
        except KeyError as e:
            print(e)

        return response

    
    def __exit__(self, exc_type, exc_value, traceback):
        with open(ClientRateLimiterKeys.LEAKYBUCKET, "wb") as file:
            pickle.dump(self.rate_limiter, file)
        return False


    async def asnyc_get_data_from_test_api(self, options):
        TEST_URL = "http://127.0.0.1:5000"
        

        async with aiohttp.ClientSession() as session:
            await self.rate_limiter.acceptable_request()
            async with session.get(TEST_URL) as resp:

                if resp.status == 429:
                    raise aiohttp.ClientResponseError(status=resp.status)

                rate1, rate2 = resp.headers["X-App-Rate-Limit"]

                self._rate_limiter # ...
                

                return resp.content


